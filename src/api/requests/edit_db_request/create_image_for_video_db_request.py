from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


class CreateImageForVideoDbRequest(BaseModel):
    id_night: int
    id_filter: int
    frame_number: Optional[int] = 0
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    zip: Optional[bool] = True
    flag_info: Optional[bool] = False
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    dark: Optional[bool] = False
    hist: Optional[bool] = False
    bins: Optional[int] = 100
    remove_single_pixels: Optional[bool] = False
    use_correct_matrix: Optional[bool] = False
    multiplication_on_correct_matrix: Optional[bool] = True
    rayleigh: Optional[bool] = False
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    upper_limit: Optional[float] = 500.
    lower_limit: Optional[float] = None
    type_diff: Optional[int] = 1
    general_title: Optional[str] = None
    frame_title: Optional[bool] = False
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    data_index: Optional[int] = None,
    file_name: Optional[str] = "buf"
    save_folder: Optional[str] = "buf"
    result_matrix_safe_folder: Optional[str] = None



class CreateImageForVideoDbInternal(CreateImageForVideoDbRequest):
    files_path: Optional[List[Path]] = None
    correct_matrix_path: Optional[Path] = None