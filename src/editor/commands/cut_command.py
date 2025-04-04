from src.editor.commands.base_command import BaseCommand
from src.graphics import cut_img


class CutCommand(BaseCommand):

    def __init__(self, editor, percent_to_trim=0.1):
        super().__init__(editor)
        self.percent_to_trim = percent_to_trim


    def execute(self) -> bool:
        self.saveBackup()

        data = cut_img(self._editor.target_img.data)
        data_result = cut_img(self._editor.result_img)

        self._editor.target_img.data = data
        self._editor.result_img = data_result

        return True

