from typing import List, Optional

from pydantic import BaseModel


class CreateImageForVideoRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    frame_number: Optional[int] = 0
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    frame_title: Optional[bool] = False
    save_folder: Optional[str] = "buf"
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