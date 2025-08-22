import copy

import numpy as np

from src.models.images_models.img_data_model import ImgData
from src.utils.editor.command_history import CommandHistory
from src.utils.editor.commands.base_command import BaseCommand


class Editor:
    _instance = None
    _history: CommandHistory

    datas: list[ImgData]

    dark_start_end_index : int|None = None
    dark_end_start_index : int|None = None

    target_index: int = 0

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

        self.target_img = copy.deepcopy(self.datas[index])
        self.target_index = index
        self.result_img = self.target_img.data.copy()


    def clear(self):
        self.datas = []
        self.target_index = 0
        self.target_img = None
        self.result_img = None


    def get_target_index(self) -> int:
        return self.target_index


    def view(self):
        return self.result_img, self.target_img
