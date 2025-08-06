import os
import pickle

from src.models.dark_data_model import DarkData
from src.file.file import FitsInfoBase
from src.graphics import graphics, auto_contrast_skimage
from src.logics import logicks
from src.models.imges.abstract_img import AbstractImg


class Img(AbstractImg):

    def __init__(self, data, fit_format, data_index=None):
        self._data = data
        self._view_data = None
        self.data_rayleigh = None
        self.data_index = data_index
        self.fit_format: FitsInfoBase = fit_format
        self.filename: str|None = None

    @property
    def data(self):
        if self.data_index is None: return self._data
        return self._data[self.data_index]

    @data.setter
    def data(self, value):
        if self.data_index is None:
            self._data = value
        else:
            self._data[self.data_index] = value

    @property
    def view_data(self):
        if self._view_data is None:
            return self.data
        return self._view_data

    def remove_single_pixels(self) -> 'Img':
        self.data = graphics.remove_single_pixels(self.data, False, False, False)
        return self

    def dark_frames(self, dark_start: DarkData, dart_end: DarkData) -> 'Img':
        time = self.fit_format.get_datetime()
        self.data = logicks.subtract_noise_frame(
            dark_start.frame, dart_end.frame,
            dark_start.time, dart_end.time,
            self.data, time
        )
        return self

    def correct_matrix(self, correct_matrix, multiplication=True) -> 'Img':
        if multiplication:
            self.data = self.data * correct_matrix
        else:
            self.data = self.data / correct_matrix
        return  self

    def rayleigh(self) -> 'Img':
        self.data_rayleigh = graphics.calculate_frame_Rayleigh(self.data, self.fit_format, False)
        return self

    def cut(self, percent_to_trim=0.1, nan=True) -> 'Img':
        self.data = graphics.cut_img(self.data, percent_to_trim=percent_to_trim, nan=nan)
        return self

    def auto_contrast_version(self, auto_contrast_percentiles=tuple[2, 98]) -> list:
        self._view_data, _, _ = auto_contrast_skimage(self.data, auto_contrast_percentiles=auto_contrast_percentiles)
        return self.view_data

    def save_rayleigh_matrix(self, folder: str) -> None:
        if not os.path.exists(folder):
            os.makedirs(folder)

        if self.filename is None or len(self.filename)==0:
            self.filename = self.fit_format.get_datetime()

        save_path = (
            os.path.join(
                folder, f"{self.filename}.pkl"
            )
        )

        with open(save_path, 'wb') as file:
            pickle.dump(self.data_rayleigh, file)
