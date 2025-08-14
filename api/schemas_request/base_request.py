from typing import Optional, List

from pydantic import BaseModel


# Создаём модель для входных данных
class CreateVideoRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    first_frame_number: Optional[int] = 0
    last_frame_number: Optional[int] = None
    name_file: Optional[str] = "output"
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    cut: Optional[bool] = False
    frame_title: Optional[bool] = False
    save_folder: Optional[str] = ""
    save_folder_video: Optional[str] = None
    save_img: Optional[bool] = False
    name_img_folder: Optional[str] = "img_for_video"
    name_video_folder: Optional[str] = "video"
    dark: Optional[bool] = False
    dark_file_name: Optional[str] = "DARK"
    fit_format: Optional[str] = "FitsInfo"
    zipped_file: Optional[bool] = True
    hist: Optional[bool] = False
    remove_single_pixels: Optional[bool] = False
    correct_matrix_path: Optional[str] = None
    multiplication_on_correct_matrix: Optional[bool] = True
    rayleigh: Optional[bool] = False
    result_matrix_safe_folder: Optional[str] = None
    type_diff: Optional[int] = 1
    upper_limit: Optional[float] = 500.
    lower_limit: Optional[float] = None
    logfun: Optional[str] = None
    counts_checks: Optional[int] = 4
    check_frame: List[int] = None
    bins: Optional[int] = 5000
    fps: Optional[float] = 1
    frames_s: Optional[int] = 1
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    data_index: Optional[int] = None


class GetDarkFilesRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    dark_file_name: Optional[str] = "DARK"
    zipped_file: Optional[bool] = True
    fit_format: Optional[str] = "FitsInfo"
    save_folder: Optional[str] = "buf"
    file_name: Optional[str] = 'buf'



# Модель запроса
class CreateImageForVideoRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    frame_number: Optional[int] = 0
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    frame_title: Optional[bool] = False
    save_folder: Optional[str] = None
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    dark: Optional[bool] = False
    dark_name: Optional[str] = "DARK"
    zip: Optional[bool] = True
    hist: Optional[bool] = True
    remove_single_pixels: Optional[bool] = False
    correct_matrix: Optional[str] = None
    multiplication_on_correct_matrix: Optional[bool] = True
    Rayleigh: Optional[bool] = False
    result_matrix_safe_folder: Optional[str] = None
    type_diff: Optional[int] = 1
    upper_limit: Optional[float] = 500.
    lower_limit: Optional[float] = None
    bins: Optional[int] = 5000
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    logfun: Optional[str] = None  # Или замените на нужный тип
    data_index: Optional[int] = None,
    file_name: Optional[str] = "buf"


# Модель запроса
class CreateImageRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    frame_number: Optional[int] = 0
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    save_folder: Optional[str] = None
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    dark: Optional[bool] = False
    dark_file_name: Optional[str] = "DARK"
    zipped_file: Optional[bool] = True
    remove_single_pixels: Optional[bool] = False
    correct_matrix_path: Optional[str] = None
    multiplication_on_correct_matrix: Optional[bool] = True
    rayleigh: Optional[bool] = False
    result_matrix_save_folder: Optional[str] = None
    check_frame: Optional[int] = None
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    logfun: Optional[str] = None  # Или замените на нужный тип
    data_index: Optional[int] = None,
    file_name: Optional[str] = "buf"



class CreateHeatmapRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    first_frame_number: Optional[int] = 0
    last_frame_number: Optional[int] = None
    edges: Optional[int] = 0
    flag_info: Optional[bool] = False
    title: Optional[str] = None
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    save_folder: Optional[str] = None
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    dark: Optional[bool] = False
    dark_file_name: Optional[str] = "DARK"
    zipped_file: Optional[bool] = True
    remove_single_pixels: Optional[bool] = False
    correct_matrix_path: Optional[str] = None
    multiplication_on_correct_matrix: Optional[bool] = True
    rayleigh: Optional[bool] = False
    counts_checks: Optional[int] = 4
    check_frame: Optional[int] = None
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    result_auto_contrast: Optional[bool] = True
    bins: Optional[int] = 500
    cmap: Optional[str] = "viridis"
    logfun: Optional[str] = None  # Или замените на нужный тип
    data_index: Optional[int] = None
    file_name: Optional[str] = "buf"


# Модель для ответа с изображениями
class ImagesResponse(BaseModel):
    images: List[str]

