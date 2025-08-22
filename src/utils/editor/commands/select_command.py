
from src.utils.editor.commands.base_command import BaseCommand
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.editor.editor import Editor

class SelectCommand(BaseCommand):

    def __init__(self, editor: 'Editor', index: int):
        super().__init__(editor)
        self.index = index

    def execute(self) -> bool:
        self.saveBackup()

        self._editor.select_img(self.index)

        return True

