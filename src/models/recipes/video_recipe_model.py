import cv2
from matplotlib import pyplot as plt

from src import logics
from src.models.recipes.base_recipes_model import BaseRecipes


class VideoRecipe(BaseRecipes):
    first_frame_number: int = 0
    last_frame_number: int | None = None
    counts_checks: int = 1
    check_frame: list[int]|None = None
    bins: int = 100

    xmin_data: float | None = None
    xmax_data: float | None = None
    ymin_data: float | None = None
    ymax_data: float | None = None
    xmin_diff: float | None = None
    xmax_diff: float | None = None
    ymax_diff: float | None = None

    def __init__(self, names_files,  root_path: str, correct_matrix_path=None):
        self.names_files: list[str] = names_files
        self.root_path: str = root_path
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

    def found_limits(self):
        (self.xmin_data, self.xmax_data,
         self.ymin_data, self.ymax_data,
         self.xmin_diff, self.xmax_diff, self.ymax_diff) = logics.get_hist_p(
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

