from typing import Any

import cv2
from matplotlib import pyplot as plt

from src.file.file import FitsInfoBase, FitsInfo
from src.models.dark_data_model import DarkData
from src.models.imges.abstract_img import AbstractImg
from src.models.imges.img_model import Img
from src.models.recipes.video_recipe_model import VideoRecipe


class DuoImg(AbstractImg):

    def __init__(self, img_first: Img|None = None, img_second: Img|None = None):
        self.img_first: Img|None = img_first
        self.img_second: Img|None = img_second
        self._view_data = None

    @property
    def data(self) -> tuple[Img|None, Img|None]:
        return self.img_first.data, self.img_second.data

    @property
    def fit_format(self) -> FitsInfoBase:
        return self.img_first.fit_format

    @property
    def view_data(self):
        if self._view_data is None:
            return self.data #need fix
        return self._view_data

    @view_data.setter
    def view_data(self, new_view):
        self._view_data = new_view

    def remove_single_pixels(self) -> 'DuoImg':
        self.img_first.remove_single_pixels()
        self.img_second.remove_single_pixels()
        return self

    def dark_frames(self, dark_start: DarkData, dart_end: DarkData) -> 'DuoImg':
        self.img_first.dark_frames(dark_start, dart_end)
        self.img_second.dark_frames(dark_start, dart_end)
        return self

    def correct_matrix(self, correct_matrix, multiplication=True) -> 'DuoImg':
        self.img_first.correct_matrix(correct_matrix, multiplication)
        self.img_second.correct_matrix(correct_matrix, multiplication)
        return self

    def rayleigh(self) -> 'DuoImg':
        self.img_first.rayleigh()
        self.img_second.rayleigh()
        return self

    def cut(self, percent_to_trim=0.1, nan=True ) -> 'DuoImg':
        self.img_first.cut()
        self.img_second.cut()
        return self

    def auto_contrast_version(self, auto_contrast_percentiles=tuple[2, 98]) -> list:
        self.img_first.auto_contrast_version(auto_contrast_percentiles=auto_contrast_percentiles)
        self.img_second.auto_contrast_version(auto_contrast_percentiles=auto_contrast_percentiles)
        return []


    def save_rayleigh_matrix(self, folder: str, filename: str) -> None:
        self.img_first.save_rayleigh_matrix(folder)
        self.img_second.save_rayleigh_matrix(folder)


    def show(self, recipe: VideoRecipe):
        img = cv2.cvtColor(self.view_data, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=recipe.figsize, dpi=100)
        plt.imshow(img)
        plt.axis('off')
        plt.show()

    def get_diff(self) -> list:
        return self.img_first.data - self.img_second.data