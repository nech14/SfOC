import copy
import os
import pickle
from datetime import datetime
from pathlib import Path

from src.models.common_models.dark_data_model import DarkData
from src.models.fits_models.abstract_fits import FitsInfoAbstract
from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.pipeline.utils.graphics_helpers import auto_contrast_skimage
from src.utils.graphics import old_graphics
from src.utils.logics.work_with_dark import subtract_noise_frame


class Img(AbstractImg):
    def __init__(self, data, fit_format, data_index=None):
        self._data = data
        self._view_data = None
        self.data_rayleigh = None
        self.data_index = data_index
        self.fit_format: FitsInfoAbstract = fit_format
        self.filename: str | None = None

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

    def get_datetime(self) -> datetime:
        return self.fit_format.get_datetime()

    def remove_single_pixels(self) -> 'Img':
        self.data = old_graphics.remove_single_pixels(self.data, False, False, False)
        return self

    def dark_frames(self, dark_start: DarkData, dart_end: DarkData) -> 'Img':
        time = self.fit_format.get_datetime()
        self.data = subtract_noise_frame(
            dark_start, dart_end,
            self.data, time
        )
        return self

    def dark_frames_by_recipe(self, recipe: BaseRecipes) -> 'Img':
        return self.dark_frames(recipe.dark_start, recipe.dart_end)

    def correct_matrix(self, correct_matrix, multiplication=True) -> 'Img':
        if multiplication:
            self.data = self.data * correct_matrix
        else:
            self.data = self.data / correct_matrix
        return self

    def rayleigh(self) -> 'Img':
        self.data_rayleigh = old_graphics.calculate_frame_Rayleigh(self.data, self.fit_format, False)
        return self

    def no_rayleigh(self) -> 'AbstractImg':
        self.data_rayleigh = copy.deepcopy(self.data)
        return self

    def cut(self, percent_to_trim=0.1, nan=True) -> 'Img':
        self.data = old_graphics.cut_img(self.data, percent_to_trim=percent_to_trim, nan=nan)
        return self

    def auto_contrast_version(self, auto_contrast_percentiles=tuple[2, 98]) -> list:
        self._view_data, _, _ = auto_contrast_skimage(self.data,
                                                      auto_contrast_percentiles=auto_contrast_percentiles)  # Вынести в модуль!
        return self.view_data

    def save_rayleigh_matrix(self, folder: str, filename: str) -> Path:
        if not os.path.exists(folder):
            os.makedirs(folder)

        if filename is None or len(filename) == 0:
            if self.filename is None or len(self.filename) == 0:
                filename = self.fit_format.get_datetime()
            else:
                filename = self.filename

        save_path = (
            os.path.join(
                folder, f"{filename}.pkl"
            )
        )

        with open(save_path, 'wb') as file:
            pickle.dump(self.data_rayleigh, file)

        return Path(save_path)
