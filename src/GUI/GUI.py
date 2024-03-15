import os
import pdb
from pathlib import Path
from asyncio import Queue
from typing import Iterable

import numpy as np
from textual.app import App, ComposeResult
from textual.await_complete import AwaitComplete
from textual.screen import Screen
from textual.widgets import DirectoryTree, Footer, Header, Static
from textual.widgets._directory_tree import DirEntry

import psutil
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
                    ("enter", "select_cursor", "Select"),
                     ("<", "last_disk", "Last disk"),
                     (">", "next_disk", "Next disk")]
    else:
        BINDINGS = [("i", "up", 'Up'),
                    ("enter", "select_cursor", "Select")]

    number_disk = 0
    main_title = None
    selected = np.array([])


    def action_up(self) -> None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        print("Current Directory:", current_directory)

        self.update_path(current_directory)

    def action_select_cursor(self):
        line = self._tree_lines[self.cursor_line]
        path = str(line.path[-1].data.path)
        if len(self.selected)==0 or not path in self.selected:
            self.selected = np.append(self.selected, path)
        else:
            mask = self.selected != path
            self.selected = self.selected[mask]

        global ERROR_TEXT
        ERROR_TEXT = str(self.selected)

        global app
        TEXT = str(self.selected)
        #TEXT = str(line)
        app.widget.update(TEXT)


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
        yield Static(ERROR_TEXT)
        yield Static("Press any key to continue [blink]_[/]", id="any-key")


TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""

class DirectoryTreeApp(App):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    root_directory = os.path.dirname(parent_directory)

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("k", "push_screen('bsod')", "K")]

    CSS_PATH = "background_transparency.tcss"

    widget = Static(TEXT)

    def compose(self) -> ComposeResult:
        yield FilteredDirectoryTree(self.root_directory)
        yield self.widget
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_mount(self) -> None:
        self.install_screen(BSOD(), name="bsod")


app = DirectoryTreeApp()

def start():
    app.run()
