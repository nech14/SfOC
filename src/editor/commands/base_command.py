
from abc import  ABC, abstractmethod

from src.editor.editor import Editor
from src.models.img_data import ImgData


class BaseCommand(ABC):

    _editor: Editor
    _backup: ImgData = None
    _backup_datas = None

    def __init__(self, editor):
        self._editor = editor

    def saveBackup(self):
        self._backup_datas = self._editor.datas
        self._backup = self._editor.target_img

    def undo(self):
        self._editor.datas = self._backup_datas
        self._editor.target_img = self._backup

    @abstractmethod
    def execute(self) -> bool:
        pass

