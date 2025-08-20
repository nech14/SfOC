from typing import List, Optional

from pydantic import BaseModel


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
    fit_format: Optional[str] = "FitsInfo"
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