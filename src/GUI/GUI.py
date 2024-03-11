
import os
import pdb
from pathlib import Path
from typing import Iterable

import textual
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import DirectoryTree, Footer, Header, Static


ERROR_TEXT = """
An error has occurred. To continue:

Press Enter to return to Windows, or

Press CTRL+ALT+DEL to restart your computer. If you do this,
you will lose any unsaved information in all open applications.

Error: 0E : 016F : BFF9B3D4
"""


class FilteredDirectoryTree(DirectoryTree):

    BINDINGS = [("i", "up", 'Up')]


    def action_up(self) -> None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        #self.PATH =  '/'
        self.path = current_directory
        self.reload()
        global ERROR_TEXT
        ERROR_TEXT = str(self.path)



class BSOD(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" Windows ", id="title")
        yield Static(ERROR_TEXT)
        yield Static("Press any key to continue [blink]_[/]", id="any-key")


class DirectoryTreeApp(App):

    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    root_directory = os.path.dirname(parent_directory)

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("k", "push_screen('bsod')", "K")]


    aaa = FilteredDirectoryTree(root_directory)

    def compose(self) -> ComposeResult:
        yield self.aaa
        yield Header()
        yield Footer()


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
        self.root_directory = os.path.dirname(self.parent_directory)


    def on_mount(self) -> None:
        self.install_screen(BSOD(), name="bsod")


def start():
    app = DirectoryTreeApp()
    app.run()