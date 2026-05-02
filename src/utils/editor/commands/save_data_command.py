import os.path
import pickle

from src.utils.editor.commands.base_command import BaseCommand


class SaveDataCommand(BaseCommand):

    def __init__(self, editor, save_folder:str, name_file:str=None):
        super().__init__(editor)
        self.name_file = name_file
        self.save_folder = save_folder


    def execute(self) -> bool:

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        if self.name_file is None:
            self.name_file = f"{self._editor.target_img.name}_result_matrix"

        result_matrix_safe_folder_data = os.path.join(self.save_folder, f"{self.name_file}.pkl")
        with open(result_matrix_safe_folder_data, 'wb') as f:
            pickle.dump(
                self._editor.target_img.data,
                f
            )


        return False

