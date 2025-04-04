from src.editor.commands.base_command import BaseCommand
from src.graphics import auto_contrast_skimage


class AutoContrastCommand(BaseCommand):

    def __init__(self, editor, auto_contrast_percentiles=[2, 98]):
        super().__init__(editor)
        self.auto_contrast_percentiles = auto_contrast_percentiles

    def execute(self) -> bool:
        self.saveBackup()

        data = auto_contrast_skimage(self._editor.target_img.data, self.auto_contrast_percentiles)

        self._editor.target_img.data = data

        return True

