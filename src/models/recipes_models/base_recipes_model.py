
from datetime import datetime
from pathlib import Path
import numpy as np
from pydantic import BaseModel

from src.api.requests.edit_db_request.create_image_db_request import CreateImageDbRequest
from src.api.requests.edit_request.create_heatmap_request import CreateHeatmapRequest
from src.api.requests.edit_request.create_image_for_video_request import CreateImageForVideoRequest
from src.api.requests.edit_request.create_image_request import CreateImageRequest
from src.api.requests.edit_request.create_video_request import CreateVideoRequest
from src.models.common_models.dark_data_model import DarkData
from src.models.fits_models.abstract_fits import FitsInfoAbstract
from src.models.fits_models.fits import FitsInfo
from src.utils.common.common import get_vars_str
from src.utils.common.fits_formats import fits_formats
from src.utils.file import file
from src.utils.logics.work_with_correct_matrix import create_correct_matrix
from src.utils.logics.work_with_dark import get_dark_avg, get_dark_by_path


class BaseRecipes:
    files_names: list[str] = []
    root_path: Path
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
    correct_matrix_path: Path = None
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

    def get_frames_len(self):
        if self.files_path is None or len(self.files_path) == 0:
            self.get_path_files()
        if len(self.files_names) > 0:
            return len(self.files_names)
        if len(self.files_path) > 0:
            return len(self.files_path)
        return 0


    def open_correct_matrix(self):
        # self.correct_matrix = graphics.create_correct_matrix(2, 2048, self.correct_matrix_path)
        self.correct_matrix = create_correct_matrix(
            self.correct_matrix_path,
            2,
            2048,
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

    def open_dark_by_datetime(
            self,
            need_time: datetime | tuple[datetime, datetime]
    ) -> tuple[DarkData, DarkData]:
        if isinstance(need_time, tuple):
            return self._open_dark_two_dates(*need_time)
        else:
            return self._open_dark_one_date(need_time)


    def _open_dark_one_date(self, dt) -> tuple[DarkData, DarkData]:
        dates_np = np.array([e.time for e in self.dark_data])
        mask = (dates_np[:-1] <= dt) & (dt <= dates_np[1:])
        idx = np.where(mask)[0]
        i = idx[0]
        self.dark_start = self.dark_data[i]
        self.dart_end = self.dark_data[i + 1]
        return self.dark_start, self.dart_end


    def _open_dark_two_dates(self, dt1, dt2):
        raise NotImplementedError


    def get_dark_files(self) -> list[DarkData]:
        if len(self.dark_file_path) > 0:
            self.dark_data = get_dark_by_path(
                self.dark_file_path,
                self.zipped_file,
                self.fit_format
            )
        elif len(self.dark_data) == 0:
            self.open_dark()
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
            |CreateImageDbRequest|BaseModel
    ):
        if ((hasattr(request, "files_list") and hasattr(request, "data_path"))
                and cls.__name__ in ["ImageRecipe", "VideoRecipe"]):
            recipe = cls(request.files_list, request.data_path)
        else:
            recipe = cls()

        if hasattr(request, "data_path") and request.data_path is not None:
            recipe.root_path = request.data_path

        if hasattr(request, "data_path") and request.data_path is not None:
            recipe.names_files = request.files_list

        if hasattr(request, "files_path") and request.files_path is not None:
            recipe.files_path = request.files_path

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


    def __str__(self) -> str:
        return get_vars_str(self)