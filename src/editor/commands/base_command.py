
from abc import  ABC, abstractmethod

from src.editor.editor import Editor


class BaseCommand(ABC):

    __editor: Editor
    __data = []

    def __init__(self):
        pass


    @abstractmethod
    def execute(self) -> bool:
        pass

