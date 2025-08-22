from abc import ABC, abstractmethod
from datetime import datetime

import matplotlib.pyplot as plt

from src.models.common_models.dark_data_model import DarkData
from src.models.fits_models.abstract_fits import FitsInfoAbstract
from src.models.recipes_models.base_recipes_model import BaseRecipes


class AbstractImg(ABC):

    filename: str|None = None
    fit_format: FitsInfoAbstract|None = None

    @property
    @abstractmethod
    def data(self):
        pass

    @property
    @abstractmethod
    def view_data(self):
        pass

    @abstractmethod
    def remove_single_pixels(self) -> 'AbstractImg':
        pass

    @abstractmethod
    def dark_frames(self, dark_start: DarkData, dart_end: DarkData) -> 'AbstractImg':
        pass

    @abstractmethod
    def dark_frames_by_recipe(self, recipe: BaseRecipes) -> 'AbstractImg':
        pass

    @abstractmethod
    def correct_matrix(self, correct_matrix, multiplication=True) -> 'AbstractImg':
        pass

    @abstractmethod
    def rayleigh(self) -> 'AbstractImg':
        pass

    @abstractmethod
    def cut(self, percent_to_trim=0.1, nan=True) -> 'AbstractImg':
        pass

    @abstractmethod
    def auto_contrast_version(self, auto_contrast_percentiles=tuple[2, 98]) -> list:
        pass

    @abstractmethod
    def save_rayleigh_matrix(self, folder: str, filename: str) -> None:
        pass

    @abstractmethod
    def get_datetime(self) -> datetime:
        pass

    def show(self, recipe: BaseRecipes) -> None:
        plt.imshow(self.view_data)
        plt.show()