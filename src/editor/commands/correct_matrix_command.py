import numpy as np

from src.editor.commands.base_command import BaseCommand


class CorrectMatrixCommand(BaseCommand):

    def __init__(self, editor, corr_matrix, multiplication_on_correct_matrix=True):
        super().__init__(editor)
        self.corr_matrix = corr_matrix
        self.multiplication_on_correct_matrix = multiplication_on_correct_matrix


    def execute(self) -> bool:
        self.saveBackup()

        if self.multiplication_on_correct_matrix:
            data = self._editor.target_img.data * self.corr_matrix.astype(np.float64)
        else:
            data = self._editor.target_img.data / self.corr_matrix.astype(np.float64)


        data[data < 0] = np.nan

        self._editor.target_img.data = data

        return True


