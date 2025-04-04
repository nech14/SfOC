import numpy as np

from src.editor.commands.base_command import BaseCommand
from src.editor.command_history import CommandHistory
from src.models.img_data import ImgData


class Editor:
    _instance = None
    _history: CommandHistory

    datas: list[ImgData]

    target_img: ImgData|None
    result_img: np.array

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Editor, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.datas = []
        self.target_img = None
        self.result_img = None
        self._history = CommandHistory()


    def executeCommand(self, command: BaseCommand):
        if command.execute():
            self._history.push(command)


    def undo(self):
        command = self._history.pop()
        if command is not None:
            command.undo()


    def select_img(self, index:int):
        if len(self.datas) == 0 or not 0 < index < len(self.datas):
            return

        self.target_img = self.datas[index]
        self.result_img = self.target_img.data.copy()


    def clear(self):
        self.datas = []
        self.target_img = None
        self.result_img = None


    def view(self):
        return self.result_img, self.target_img
