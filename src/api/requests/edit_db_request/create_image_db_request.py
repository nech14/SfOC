from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel, Field, PrivateAttr


class CreateImageDbRequest(BaseModel):
    frameId: int
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"
    dark: Optional[bool] = False
    remove_single_pixels: Optional[bool] = False
    use_correct_matrix: Optional[bool] = True
    multiplication_on_correct_matrix: Optional[bool] = True
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    data_index: Optional[int] = None,
    zipped_file: Optional[bool] = True
    file_name: Optional[str] = "buf"
    save_folder: Optional[str] = None
    result_matrix_save_folder: Optional[str] = None



class CreateImageDbInternal(CreateImageDbRequest):
    files_path: Optional[List[Path]] = None
    frame_number: Optional[int] = 0
    correct_matrix_path: Optional[Path] = None

