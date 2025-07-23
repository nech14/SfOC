
from abc import  ABC, abstractmethod
from src.models.img_data_model import ImgData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.editor.editor import Editor


class BaseCommand(ABC):

    _editor: 'Editor'
    _backup: ImgData = None
    _backup_result: list = None
    _backup_datas: list = None
    _target_index: int|None = None

    def __init__(self, editor: 'Editor'):
        self._editor = editor

    def saveBackup(self):
        self._backup_datas = self._editor.datas.copy()
        self._backup = self._editor.target_img
        self._backup_result = self._editor.result_img
        self._target_index = self._editor.target_index

    def undo(self):
        self._editor.datas = self._backup_datas
        self._editor.target_img = self._backup
        self._editor.result_img = self._backup_result
        self._editor.target_index = self._target_index

    @abstractmethod
    def execute(self) -> bool:
        pass

