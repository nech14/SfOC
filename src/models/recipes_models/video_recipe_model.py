from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.models.common_models.dark_data_model import DarkData
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.utils.logics import old_logicks


class VideoRecipe(BaseRecipes):
    first_frame_number: int = 0
    last_frame_number: int | None = None
    counts_checks: int = 1
    check_frame: list[int]|None = None
    bins: int = 100

    dark_first_frame: tuple[DarkData, DarkData] = None
    dark_second_frame: tuple[DarkData, DarkData] = None

    xmin_data: float | None = None
    xmax_data: float | None = None
    ymin_data: float | None = None
    ymax_data: float | None = None
    xmin_diff: float | None = None
    xmax_diff: float | None = None
    ymax_diff: float | None = None

    def __init__(self, names_files: list[str]=None,  root_path: Path=None, correct_matrix_path:Path=None):
        self.names_files: list[str] = names_files
        self.root_path: Path = root_path
        self.auto_contrast = True
        self.cut = True
        self.remove_single_pixels: bool = True
        self.multiplication_on_correct_matrix: bool = True
        self.dark: bool = False
        self.dark_file_name: str = "DARK"
        self.hist: bool = True
        self.first_frame_number = 30
        self.last_frame_number = 50
        self.save_folder: str|None = None #"video_test"
        self.save_folder_video = "video_t"
        self.name_file_video = "video"
        self.fps = 30/60
        self.file_name: str|None = None
        self.frame_name: str|None = None

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

    def found_limits(self):
        (self.xmin_data, self.xmax_data,
         self.ymin_data, self.ymax_data,
         self.xmin_diff, self.xmax_diff, self.ymax_diff) = old_logicks.get_hist_p(
            self.names_files, self.root_path,
            start_i=self.first_frame_number,
            end_i=self.last_frame_number,
            _zip=self.zipped_file,
            counts_checks=self.counts_checks, bins=self.bins,
            cut=self.cut, percent_to_trim=self.percent_to_trim,
            fit_format=self.fit_format,
            dark=self.dark, dark_name=self.dark_file_name,
            corr_matrix=self.correct_matrix, Rayleigh=self.rayleigh,
            flag_info=self.flag_info, check_frame=self.check_frame,
            data_index=self.data_index,
            remove_single_pixels=self.remove_single_pixels,
            multiplication_on_correct_matrix=self.multiplication_on_correct_matrix
        )

    def show_image(self, data) -> None:
        img = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=self.figsize, dpi=100)
        plt.imshow(img)
        plt.axis('off')
        plt.show()

