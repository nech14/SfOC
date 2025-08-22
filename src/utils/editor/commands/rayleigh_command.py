from src.utils.editor.commands.base_command import BaseCommand
from src.utils.graphics.old_graphics import calculate_frame_Rayleigh


class RayleighCommand(BaseCommand):

    def __init__(self, editor):
        super().__init__(editor)


    def execute(self) -> bool:
        self.saveBackup()

        data = calculate_frame_Rayleigh(
            self._editor.target_img.data,
            self._editor.target_img.info,
            False
        )

        self._editor.target_img.data = data  # rework for view and data

        return True