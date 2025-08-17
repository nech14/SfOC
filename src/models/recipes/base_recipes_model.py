import numpy as np

from src.api.base_api import CreateImageRequest, CreateHeatmapRequest, CreateImageForVideoRequest
from src.api.schemas_request.base_request import CreateVideoRequest
from src.file import file
from src.file.file import FitsInfoBase, FitsInfo
from src.graphics import graphics
from src.logics.logicks import get_dark_avg
from src.models.dark_data_model import DarkData
from src.file.file import class_registry

class BaseRecipes:
    names_files: list[str]|None = None
    root_path: str
    frame_number: int
    flag_info: bool = False
    name: str|None = None
    cut: bool = False
    percent_to_trim: float = 0.1
    save_folder: str = "result"
    figsize: tuple[float, float] | None = None
    fit_format: type[FitsInfoBase] = FitsInfo
    dark: bool = False
    dark_file_name: str = "DARK"
    zipped_file: bool = True
    remove_single_pixels: bool = False
    correct_matrix_path: str = None
    rayleigh: bool = False
    result_matrix_save_folder: str = None
    logfun = None
    data_index: int = None
    file_name: str = "result1252"
    multiplication_on_correct_matrix: bool = False
    auto_contrast: bool = False
    auto_contrast_percentiles: tuple[int, int] = [2, 98]
    show: bool = False


    correct_matrix = None
    dark_start: DarkData = None
    dart_end: DarkData = None

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

    @classmethod
    def get_recipe_by_request(
            cls, request: CreateImageRequest|CreateHeatmapRequest|CreateImageForVideoRequest|CreateVideoRequest
    ):
        if cls.__name__ in ["ImageRecipe", "HeatmapRecipe", "VideoRecipe"]:
            recipe = cls(request.files_list, request.data_path)
        else:
            recipe = cls()

        # Только для случаев, когда названия в request и recipe разные
        rename_map = {
            "general_title": "name",
        }

        for req_attr, value in request.__dict__.items():
            if value is None:
                continue

            # Если есть переименование
            target_attr = rename_map.get(req_attr, req_attr)

            if hasattr(recipe, target_attr):
                setattr(recipe, target_attr, value)

        recipe.fit_format = class_registry[request.fit_format]

        return recipe

