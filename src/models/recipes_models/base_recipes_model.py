
from datetime import datetime
from pathlib import Path
import numpy as np
from src.api.base_api import CreateImageRequest, CreateHeatmapRequest, CreateImageForVideoRequest
from src.api.requests.edit_db_request.create_image_db_request import CreateImageDbRequest
from src.api.requests.edit_request.create_video_request import CreateVideoRequest
from src.models.common_models.dark_data_model import DarkData
from src.models.fits_models.abstract_fits import FitsInfoAbstract
from src.models.fits_models.fits import FitsInfo
from src.pipeline.utils import graphics_helpers
from src.pipeline.utils.helpers import get_dark_avg
from src.utils.common.fits_formats import fits_formats
from src.utils.file import file


class BaseRecipes:
    files_names: list[str] | None = None
    root_path: str
    files_path: list[Path] = []
    frame_number: int
    flag_info: bool = False
    name: str|None = None
    cut: bool = False
    percent_to_trim: float = 0.1
    save_folder: str = "result"
    figsize: tuple[float, float] | None = None
    fit_format: type[FitsInfoAbstract] = FitsInfo
    dark: bool = False
    dark_file_name: str = "DARK"
    dark_file_path: list[Path] = []
    dark_data: list[DarkData] = []
    zipped_file: bool = True
    remove_single_pixels: bool = False
    correct_matrix_path: str = None
    use_correct_matrix: bool = False
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
        # self.correct_matrix = graphics.create_correct_matrix(2, 2048, self.correct_matrix_path)
        self.correct_matrix = graphics_helpers.create_correct_matrix_new(
            2,
            2048
            ,Path(self.correct_matrix_path)
        )


    def open_dark(self):
        self.dark_start = get_dark_avg(
            self.files_names,
            self.root_path,
            dark_name=self.dark_file_name,
            _zip=self.zipped_file,
            fit_format=self.fit_format
        )
        self.dart_end = get_dark_avg(
            np.flip(self.files_names),
            self.root_path,
            dark_name=self.dark_file_name,
            _zip=self.zipped_file,
            fit_format=self.fit_format
        )

    def open_dark_by_datetime(self, need_time: datetime) -> tuple[DarkData, DarkData]:
        dates_np = np.array([e.time for e in self.dark_data])
        mask = (dates_np[:-1] <= need_time) & (need_time <= dates_np[1:])
        idx = np.where(mask)[0]
        i = idx[0]
        self.dark_start = self.dark_data[i]
        self.dart_end = self.dark_data[i+1]
        return self.dark_start, self.dart_end

    def get_dark_files(self) -> list[DarkData]:
        if len(self.dark_file_path) > 0:
            self.dark_data = []
            for path in self.dark_file_path:
                info, data = file.open_gz(path, _zip=self.zipped_file)
                info = self.fit_format(info)
                time = info.get_datetime()
                dark_f = DarkData(data, time)
                self.dark_data.append(dark_f)

            self.dark_data.sort(key=lambda e: e.time)
        return self.dark_data

    def get_names_files(self) -> list[str]:
        self.files_names = file.get_name_files(self.root_path)
        return self.files_names


    def get_path_files(self) -> list[Path]:
        if not self.files_names:
            self.get_names_files()

        self.files_path = [Path(self.root_path, name) for name in self.files_names]
        return self.files_path


    @classmethod
    def get_recipe_by_request(
            cls, request:
            CreateImageRequest|CreateHeatmapRequest
            |CreateImageForVideoRequest|CreateVideoRequest
            |CreateImageDbRequest
    ):
        if ((hasattr(request, "files_list") and hasattr(request, "data_path"))
                and cls.__name__ in ["ImageRecipe", "HeatmapRecipe", "VideoRecipe"]):
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

        recipe.fit_format = fits_formats[request.fit_format]

        return recipe

