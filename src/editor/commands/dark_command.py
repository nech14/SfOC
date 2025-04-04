import numpy as np
from scipy.special import result

from src.editor.commands.base_command import BaseCommand
from src.file import FitsInfo
from src.file.file import FitsInfoBase
from src.logics import get_dark, get_dark_AVG, subtract_noise_frame


class DarkCommand(BaseCommand):

    def __init__(
            self,
            editor,
            names,
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

        dark_start, dark_time_start = get_dark_AVG(
            self.names,
            self.root_path,
            dark_name = self.file_name,
            _zip = self._zip,
            fit_format = self.fit_format
        )

        dark_end, dark_time_end = get_dark_AVG(
            np.flip(self.names),
            self.root_path,
            dark_name=self.file_name,
            _zip=self._zip,
            fit_format=self.fit_format
        )

        time = self._editor.target_img.info.get_datetime()
        data = subtract_noise_frame(dark_start, dark_end, dark_time_start, dark_time_end, time)
        data = (data - data.mix()) / (data.max() - data.min())

        self._editor.target_img.data = data

        return True
