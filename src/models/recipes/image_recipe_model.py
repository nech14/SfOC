import numpy as np

from api.base_api import CreateImageRequest
from src import file
from src.file.file import FitsInfoBase, FitsInfo
from src.graphics import graphics
from src.logics.logicks import get_dark_avg
from src.models.recipes.base_recipes_model import BaseRecipes

class ImageRecipe(BaseRecipes):
    def __init__(self, names_files, root_path, correct_matrix_path=None):
        self.root_path: str = root_path
        self.names_files: list[str] = names_files
        self.frame_number: int = 20
        self.flag_info: bool = False
        self.name: str = "test124"
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
        self.result_matrix_save_folder: str|None = None
        self.logfun = None
        self.data_index: int = None
        self.file_name: str = "result12"
        self.multiplication_on_correct_matrix: bool = True
        self.auto_contrast: bool = True
        self.auto_contrast_percentiles: tuple[int, int] = [2, 98]


    @classmethod
    def create(cls):
        pass


