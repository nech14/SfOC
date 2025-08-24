from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.models.common_models.dark_data_model import DarkData
from src.models.common_models.hist_limits import HistLimits
from src.models.recipes_models.hist_recipe_model import HistRecipe

class VideoRecipe(HistRecipe):
    dark_first_frame: tuple[DarkData, DarkData] = None
    dark_second_frame: tuple[DarkData, DarkData] = None
    hist_limits: HistLimits

    def __init__(self, names_files: list[str]=(),  root_path: Path=None, correct_matrix_path:Path=None):
        self.files_names: list[str] = names_files
        self.root_path: Path = root_path
        self.auto_contrast = True
        self.cut = True
        self.remove_single_pixels: bool = True
        self.use_correct_matrix = True
        self.correct_matrix_path = correct_matrix_path
        self.multiplication_on_correct_matrix: bool = True
        self.dark: bool = False
        self.dark_file_name: str = "DARK"
        self.hist: bool = True
        self._first_frame_number = 50
        self._last_frame_number = 100
        self.save_folder: str|None = None #"video_test"
        self.save_folder_video = "video_t"
        self.name_file_video = "video"
        self.fps = 30/60
        self.file_name: str|None = None
        self.frame_name: str|None = None
        self.bins = 1000


    def _open_dark_two_dates(self, dt1: datetime, dt2: datetime) -> tuple[tuple[DarkData, DarkData], tuple[DarkData, DarkData]]:
        dates_np = np.array([e.time for e in self.dark_data])
        mask1 = (dates_np[:-1] <= dt1) & (dt1 <= dates_np[1:])
        mask2 = (dates_np[:-1] <= dt2) & (dt2 <= dates_np[1:])
        idx1 = np.where(mask1)[0]
        idx2 = np.where(mask2)[0]
        i1 = idx1[0]
        i2 = idx2[0]
        self.dark_first_frame = (self.dark_data[i1], self.dark_data[i1 + 1])
        self.dark_second_frame = (self.dark_data[i2], self.dark_data[i2 + 1])
        return self.dark_first_frame, self.dark_second_frame


    def show_image(self, data) -> None:
        img = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=self.figsize, dpi=100)
        plt.imshow(img)
        plt.axis('off')
        plt.show()

