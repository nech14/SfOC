
from src.utils.editor.commands.base_command import BaseCommand
from src.utils.graphics.old_graphics import remove_single_pixels


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

        data_result = remove_single_pixels(
            self._editor.result_img,
            False,
            False,
            False
        )

        self._editor.target_img.data = data
        self._editor.result_img = data_result

        return True
