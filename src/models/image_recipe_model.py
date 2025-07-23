import numpy as np

from src import file
from src.file.file import FitsInfoBase, FitsInfo
from src.graphics import graphics
from src.logics import get_dark_AVG
from src.logics.logicks import get_dark_avg
from src.models.dark_data_model import DarkData


class ImageRecipe:

    names_files: list[str]
    root_path: str
    frame_number: int
    flag_info: bool = False
    name: str
    cut: bool = False
    percent_to_trim: float = 0.1
    save_folder: str
    figsize: tuple[float, float] | None = None
    fit_format: type[FitsInfoBase]
    dark: bool = False
    dark_file_name: str = "DARK"
    zipped_file: bool = True
    remove_single_pixels: bool = False
    correct_matrix_path: str = None
    rayleigh: bool = False
    result_matrix_save_folder: str = None
    logfun = None
    data_index: int = None
    file_name: str = "result"
    multiplication_on_correct_matrix: bool = False
    auto_contrast: bool = True
    auto_contrast_percentiles: tuple[int, int] = [2, 98]

    correct_matrix = None
    dark_start: DarkData = None
    dart_end: DarkData = None

    def __init__(self, names_files, root_path, correct_matrix_path=None):
        self.names_files: list[str] = names_files
        self.root_path: str = root_path
        self.frame_number: int = 20
        self.flag_info: bool = False
        self.name: str = "test12"
        self.cut: bool = True
        self.percent_to_trim: float = 0.1
        self.save_folder: str = "result"
        self.figsize: tuple[float, float] | None = None
        self.fit_format: type[FitsInfoBase] = FitsInfo
        self.dark: bool = True
        self.dark_file_name: str = "DARK"
        self.zipped_file: bool = True
        self.remove_single_pixels: bool = False
        self.correct_matrix_path: str = correct_matrix_path
        self.rayleigh: bool = False
        self.result_matrix_save_folder: str = None
        self.logfun = None
        self.data_index: int = None
        self.file_name: str = "result12"
        self.multiplication_on_correct_matrix: bool = True
        self.auto_contrast: bool = True
        self.auto_contrast_percentiles: tuple[int, int] = [2, 98]


    @classmethod
    def create(cls):
        pass

    def open_correct_matrix(self):
        self.correct_matrix = graphics.create_correct_matrix(2, 2048, self.correct_matrix_path)

    def open_dark(self):
        self.dark_start = get_dark_avg(
            self.names_files,
            self.root_path,
            dark_name=self.dark_file_name,
            _zip=self.zipped_file,
            fit_format=self.fit_format
        )
        self.dart_end = get_dark_avg(
            np.flip(self.names_files),
            self.root_path,
            dark_name=self.dark_file_name,
            _zip=self.zipped_file,
            fit_format=self.fit_format
        )

    def get_names_files(self):
        self.names_files = file.get_name_file(self.root_path)