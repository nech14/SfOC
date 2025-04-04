
from src.editor.command_history import CommandHistory
from src.editor.commands.base_command import BaseCommand
from src.models.img_data import ImgData


class Editor:
    _instance = None
    _history: CommandHistory

    datas: list[ImgData]

    result = []
    target_img: ImgData

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super.__new__(cls)
        return cls._instance

    def __init__(self):
        self.datas = []


    def executeCommand(self, command: BaseCommand):
        if command.execute():
            self._history.push(command)


    def undo(self):
        command = self._history.pop()
        if command is not None:
            command.undo()