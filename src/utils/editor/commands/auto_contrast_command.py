from src.utils.editor.commands.base_command import BaseCommand
from src.utils.graphics import old_graphics


class AutoContrastCommand(BaseCommand):

    def __init__(self, editor, auto_contrast_percentiles=[2, 98]):
        super().__init__(editor)
        self.auto_contrast_percentiles = auto_contrast_percentiles

    def execute(self) -> bool:
        self.saveBackup()
        data, _, _ = old_graphics.auto_contrast_skimage(self._editor.result_img, self.auto_contrast_percentiles)

        self._editor.result_img = data

        return True

