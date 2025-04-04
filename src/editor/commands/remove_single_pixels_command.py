
from src.editor.commands.base_command import BaseCommand
from src.graphics import remove_single_pixels


class RemoveSinglePixelsCommand(BaseCommand):

    def __init__(self, editor):
        super().__init__(editor)


    def execute(self) -> bool:
        self.saveBackup()

        data = remove_single_pixels(
            self._editor.target_img.data,
            False,
            False,
            False
        )

        self._editor.target_img.data = data

        return True
