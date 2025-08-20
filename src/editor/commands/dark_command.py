import numpy as np

from src.editor.commands.base_command import BaseCommand
from src.file import FitsInfo
from src.file.file import FitsInfoBase, get_name_files
from src.logics import get_dark, get_dark_AVG, subtract_noise_frame


class DarkCommand(BaseCommand):

    def __init__(
            self,
            editor,
            names = None,
            root_path = "",
            file_name = "DARK",
            _zip = False,
            fit_format: FitsInfoBase = FitsInfo
    ):
        super().__init__(editor)
        self.names = names
        self.root_path = root_path
        self.file_name = file_name
        self._zip = _zip
        self.fit_format = fit_format


    def execute(self) -> bool:
        self.saveBackup()

        if self.names is None or len(self.names) == 0:
            self.names = get_name_files(self.root_path)


        dark_start_name = self.names.copy()
        if self._editor.dark_end_start_index is not None:
            dark_start_name = self.names[:self._editor.dark_end_start_index]

        dark_start, dark_time_start = get_dark_AVG(
            dark_start_name,
            self.root_path,
            dark_name = self.file_name,
            _zip = self._zip,
            fit_format = self.fit_format
        )


        dark_end_name = np.flip(self.names).copy()
        if self._editor.dark_start_end_index is not None:
            dark_end_name = self.names[self._editor.dark_start_end_index:]

        dark_end, dark_time_end = get_dark_AVG(
            dark_end_name,
            self.root_path,
            dark_name=self.file_name,
            _zip=self._zip,
            fit_format=self.fit_format
        )

        time = self._editor.target_img.info.get_datetime()
        data = subtract_noise_frame(dark_start, dark_end, dark_time_start, dark_time_end, self._editor.target_img.data,
                                    time)
        
        # до нормализации:
        # min_val = data.min()
        # max_val = data.max()
        # data_norm = (data - min_val) / (max_val - min_val)
        #
        # # потом:
        # restored_data = (data_norm * (max_val - min_val) + min_val).round().astype(np.int16)  # или другой тип

        # data = (data - data.max()) / (data.max() - data.min())
        # int_data = np.clip(data * 65535, 0, 65535).round().astype(np.uint16)

        data_result = subtract_noise_frame(dark_start, dark_end, dark_time_start, dark_time_end, self._editor.result_img,
                                    time)
        # min_val = data_result.min()
        # max_val = data_result.max()
        # data_norm = (data_result - min_val) / (max_val - min_val)

        # потом:
        # restored_data_result = (data_norm * (max_val - min_val) + min_val).round().astype(np.int16)  # или другой тип

        # data_result = (data_result - data_result.max()) / (data_result.max() - data_result.min())
        # int_data_result = np.clip(data_result * 65535, 0, 65535).round().astype(np.uint16)

        self._editor.target_img.data = data
        self._editor.result_img = data_result

        return True
