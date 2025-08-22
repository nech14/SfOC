from pathlib import Path

from src.models.fits_models.abstract_fits import FitsInfoAbstract
from src.models.fits_models.fits import FitsInfo
from src.models.recipes_models.base_recipes_model import BaseRecipes


class ImageRecipe(BaseRecipes):
    def __init__(self, files_names:list[str]=None, root_path: Path=None, correct_matrix_path=None):
        self.root_path: Path = root_path
        self.files_names: list[str] = files_names
        self.files_path: list[Path] = []
        self.frame_number: int = 20
        self.flag_info: bool = False
        self.name: str = "test124"
        self.cut: bool = True
        self.percent_to_trim: float = 0.1
        self.save_folder: str = "result"
        self.figsize: tuple[float, float] | None = None
        self.fit_format: type[FitsInfoAbstract] = FitsInfo
        self.dark: bool = True
        self.dark_file_name: str = "DARK"
        self.zipped_file: bool = True
        self.remove_single_pixels: bool = False
        self.correct_matrix_path: str = correct_matrix_path
        self.use_correct_matrix: bool = True
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

