import os
import pdb
from pathlib import Path
from asyncio import Queue
from typing import Iterable, Any

import numpy as np
from textual import on
from textual.app import App, ComposeResult
from textual.await_complete import AwaitComplete
from textual.containers import Horizontal, VerticalScroll, Grid, Container
from textual.dom import DOMNode
from textual.reactive import Reactive, var
from textual.screen import Screen, ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Static, Button, Label, Log, Input, SelectionList
from textual.widgets._directory_tree import DirEntry
from textual.widgets.selection_list import Selection

import psutil
from src import logics
from textual.widgets._tree import TreeNode, Tree
from textual.worker import WorkerCancelled, WorkerFailed

ERROR_TEXT = """
An error has occurred. To continue:

Press Enter to return to Windows, or

Press CTRL+ALT+DEL to restart your computer. If you do this,
you will lose any unsaved information in all open applications.

Error: 0E : 016F : BFF9B3D4
"""


def get_disk_partitions():
    partitions = psutil.disk_partitions(all=True)
    disk_list = []
    for partition in partitions:
        if partition.device and partition.mountpoint:
            disk_list.append(partition.device)
    return disk_list


class FilteredDirectoryTree(DirectoryTree):

    disks = get_disk_partitions()
    #disks = [1]
    if len(disks) > 1:
        BINDINGS = [("i", "up", 'Up'),
                    ("s", "select_save_dir", "Select save dir"),
                    ("enter", "select_cursor", "Select"),
                     ("<", "last_disk", "Last disk"),
                     (">", "next_disk", "Next disk")]
    else:
        BINDINGS = [("i", "up", 'Up'),
                    ("s", "select_save_dir", "Select save dir"),
                    ("enter", "select_cursor", "Select")]

    number_disk = 0
    main_title = None
    selected = np.array([])
    app = None

    def __init__(self, path, app=None):
        super().__init__(path)
        self.app = app

    def delete_index_selected(self, index: int):
        self.selected = np.delete(self.selected, index)

    def get_index_selected(self, text:str) -> int:
        return np.where(self.selected == text)[0][0]

    def action_up(self) -> None:
        current_directory = os.path.dirname(os.path.abspath(__file__))

        self.update_path(current_directory)

    def action_select_save_dir(self):
        line = self._tree_lines[self.cursor_line]
        path = str(line.path[-1].data.path)
        self.app.save_dir_container.update(path)

    def action_select_cursor(self):
        line = self._tree_lines[self.cursor_line]
        path = str(line.path[-1].data.path)

        if len(self.selected)==0 or not path in self.selected:
            self.selected = np.append(self.selected, path)
            self.app.add_DirContainer(path)
        else:
            mask = self.selected != path
            index = np.where(self.selected == path)[0][0]
            self.selected = self.selected[mask]
            self.app.remove_DirContainer(index=index)


    def action_next_disk(self) -> None:
        self.number_disk += 1
        if self.number_disk >= len(self.disks):
            self.number_disk = 0
        self.update_path(self.disks[self.number_disk])
        global ERROR_TEXT
        ERROR_TEXT = str(self.disks[self.number_disk]) + str(self.number_disk)

    def action_last_disk(self) -> None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.number_disk -= 1
        if self.number_disk < 0:
            self.number_disk = len(self.disks) - 1
        self.update_path(self.disks[self.number_disk])
        global ERROR_TEXT
        ERROR_TEXT = str(self.disks[self.number_disk]) + str(self.number_disk)

    def update_path(self, path, label=None) -> None:
        self.path = path
        data = DirEntry(self.PATH(self.path))
        if label is None:
            label = str(self.path)
        self.main_title = self.process_label(label)
        self.root = self._add_node(None, label=self.main_title, data=data, expand=True)
        self.reload()

    def reload(self) -> AwaitComplete:
        """Reload the `DirectoryTree` contents.

        Returns:
            An optionally awaitable that ensures the tree has finished reloading.
        """
        # Orphan the old queue...
        self._load_queue = Queue()
        # ... reset the root node ...
        processed = self.reload_node(self.root, title=self.main_title)
        # ...and replace the old load with a new one.
        self._loader()
        return processed

    def reload_node(self, node: TreeNode[DirEntry], title=None) -> AwaitComplete:
        """Reload the given node's contents.

        The return value may be awaited to ensure the DirectoryTree has reached
        a stable state and is no longer performing any node reloading (of this node
        or any other nodes).

        Args:
            node: The root of the subtree to reload.

        Returns:
            An optionally awaitable that ensures the subtree has finished reloading.
        """
        return AwaitComplete(self._reload(node, title=title))

    async def _reload(self, node: TreeNode[DirEntry], title=None) -> None:
        """Reloads the subtree rooted at the given node while preserving state.

        After reloading the subtree, nodes that were expanded and still exist
        will remain expanded and the highlighted node will be preserved, if it
        still exists. If it doesn't, highlighting goes up to the first parent
        directory that still exists.

        Args:
            node: The root of the subtree to reload.
        """
        async with self.lock:
            # Track nodes that were expanded before reloading.
            currently_open: set[Path] = set()
            to_check: list[TreeNode[DirEntry]] = [node]
            while to_check:
                checking = to_check.pop()
                if checking.allow_expand and checking.is_expanded:
                    if checking.data:
                        currently_open.add(checking.data.path)
                    to_check.extend(checking.children)

            # Track node that was highlighted before reloading.
            highlighted_path: None | Path = None
            if self.cursor_line > -1:
                highlighted_node = self.get_node_at_line(self.cursor_line)
                if highlighted_node is not None and highlighted_node.data is not None:
                    highlighted_path = highlighted_node.data.path

            if title is None:
                title = str(node.data.path.name)

            if node.data is not None:
                self.reset_node(
                    node, title, DirEntry(self.PATH(node.data.path))
                )

            # Reopen nodes that were expanded and still exist.
            to_reopen = [node]
            while to_reopen:
                reopening = to_reopen.pop()
                if not reopening.data:
                    continue
                if reopening.allow_expand and (
                        reopening.data.path in currently_open or reopening == node
                ):
                    try:
                        content = await self._load_directory(reopening).wait()
                    except (WorkerCancelled, WorkerFailed):
                        continue
                    reopening.data.loaded = True
                    self._populate_node(reopening, content)
                    to_reopen.extend(reopening.children)
                    reopening.expand()

            if highlighted_path is None:
                return

            # Restore the highlighted path and consider the parents as fallbacks.
            looking = [node]
            highlight_candidates = set(highlighted_path.parents)
            highlight_candidates.add(highlighted_path)
            best_found: None | TreeNode[DirEntry] = None
            while looking:
                checking = looking.pop()
                checking_path = (
                    checking.data.path if checking.data is not None else None
                )
                if checking_path in highlight_candidates:
                    best_found = checking
                    if checking_path == highlighted_path:
                        break
                if (
                        checking.allow_expand
                        and checking.is_expanded
                        and checking_path in highlighted_path.parents
                ):
                    looking.extend(checking.children)
            if best_found is not None:
                # We need valid lines. Make sure the tree lines have been computed:
                _ = self._tree_lines
                self.cursor_line = best_found.line


class BSOD(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" Windows ", id="title")
        yield Static(ERROR_TEXT, id="any-key")


TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""



class DirContainer(Container):
    text = "gggg"
    app = None

    def __init__(self, text, app=None):
        self.text = text
        self.app = app
        super().__init__()
        self.classes = "selected_div"

    def compose(self) -> ComposeResult:
        yield Static(self.text, classes="static_selected")
        yield Button(id="update_save_dir", classes="create_save_dir")
        yield Button(id="delete", classes="delete_button")

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        if button_id == "delete":
            if not self.app is None:
                self.app.remove_text_DirContainer(self.text)
        elif button_id == "update_save_dir":
            self.app.save_dir_container.update(self.text)
        pass


class SelectionListM(ModalScreen):
    #CSS_PATH = "selection_list.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield SelectionList[int](
                Selection("Main", 0, True),
                Selection("5577", 1),
                Selection("6300", 2),
                Selection("8400", 3),
                Selection("8465", 4),
                Selection("8570", 5),
                Selection("OH", 6, True),
                Selection("Poker", 7),
                Selection("Fighter Combat", 8, True),
            )
            with Horizontal():
                yield Button.success("Yes", id="yes")
                yield Button.error("No", id="no")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Shall we play some games?"

    @on(Button.Pressed)
    def leave_modal_screen(self, event):
        self.dismiss(event.button.id == "yes")


class YesOrNo(ModalScreen):
    def compose(self):
        with Container():
            yield Label("Are you sure?")
            with Horizontal():
                yield Button.success("Yes", id="yes")
                yield Button.error("No", id="no")

    @on(Button.Pressed)
    def leave_modal_screen(self, event):
        self.dismiss(event.button.id == "yes")


class InputYesOrNo(ModalScreen):

    text = ""
    inp = Input(value=text)

    def __init__(self, text):
        self.text = str(text)
        self.inp = Input(value=self.text)
        super().__init__()

    def compose(self):
        with Container():
            yield self.inp
            with Horizontal():
                yield Button.success("Yes", id="yes")
                yield Button.error("No", id="no")

    @on(Button.Pressed)
    def leave_modal_screen(self, event):
        if event.button.id == "yes":
            self.dismiss(self.inp.value)
        else:
            self.dismiss(None)




class DirectoryTreeApp(App):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    root_directory = os.path.dirname(parent_directory)

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("k", "push_screen('bsod')", "K"),
                #("a", "add_gg", "A"),
                ("r", "remove_gg", "Remove last"),
                ("d", "all_delete", "Delete all"),
                ("n", "update_save_dir", "Update save dir"),
                ("o", "slect_1", "O")]

    CSS_PATH = "background_transparency.tcss"


    tree = None
    save_dir_container = Label(f"{root_directory}\\data", id="save_dir")
    def __init__(self):
        self.tree = FilteredDirectoryTree(self.root_directory, self)
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.tree
        with Container():
            with Container(classes="save_dir_div"):
                yield Label("Save dir: ")
                yield self.save_dir_container
            yield VerticalScroll(id="main_buf")
        yield Header()
        yield Footer()

    def action_slect_1(self):
        self.push_screen(SelectionListM(), self.GG)

    def GG(self, bool):
        if bool:
            new_path, names = logics.get_names(self.tree.selected[-1])
            save_dir = os.path.normpath(str(self.save_dir_container.renderable))
            logics.create_heatmap(names, new_path, save_folder=save_dir, title="gggg12", auto_contrast=False, edges=15, limit=10000)
        pass

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_update_save_dir(self):
        text = self.save_dir_container.renderable
        self.push_screen(InputYesOrNo(text), self.update_dir)

    def update_dir(self, value):
        if value:
            self.save_dir_container.update(value)

    def add_DirContainer(self, text):
        cont = DirContainer(text, self)
        container = self.query_one("#main_buf")
        container.mount(cont)
        cont.scroll_visible()

    def remove_DirContainer(self, index=-1):
        conts = self.query(DirContainer)
        if conts:
            conts[index].remove()

    def remove_text_DirContainer(self, text):
        index = self.tree.get_index_selected(text)
        self.remove_DirContainer(index)
        self.tree.delete_index_selected(index)

    # def action_add_gg(self) -> None:
    #     """An action to toggle dark mode."""
    #
    #     cont = DirContainer("GGGG", self)
    #     container = self.query_one("#main_buf")
    #     container.mount(cont)
    #     cont.scroll_visible()
    #
    #     pass
        #self.VS._nodes._append(DirContainer("gggg"))

        #self.query_one(VerticalScroll).update()

        #global ERROR_TEXT
        #ERROR_TEXT = str(self.VS.displayed_children)

    def action_remove_gg(self):
        conts = self.query(DirContainer)
        if conts:
            conts.last().remove()
            self.tree.selected = self.tree.selected[:-1]

    def action_all_delete(self):
        if len(self.tree.selected) > 0:
            self.push_screen(YesOrNo(), self.all_delete_selecred)

    def all_delete_selecred(self, bool):
        if bool:
            conts = self.query(DirContainer)
            if conts:
                conts.remove()
                self.tree.selected = np.array([])

    def on_mount(self) -> None:
        self.install_screen(BSOD(), name="bsod")


app = DirectoryTreeApp()

def start():
    app.run()
