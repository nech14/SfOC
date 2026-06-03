import uuid
from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel

import config


class CreateMatrixDbRequest(BaseModel):
    frameId: int
    flag_info: Optional[bool] = False
    fit_format: Optional[str] = "FitsInfo"
    dark: Optional[bool] = False
    remove_single_pixels: Optional[bool] = False
    use_correct_matrix: Optional[bool] = True
    multiplication_on_correct_matrix: Optional[bool] = True
    data_index: Optional[int] = None,
    zipped_file: Optional[bool] = True
    rayleigh: Optional[bool] = False



class CreateMatrixDbRequestInternal(CreateMatrixDbRequest):
    general_title: Optional[str] = None #?
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    auto_contrast: Optional[bool] = False
    auto_contrast_percentiles: List[int] = [2, 98]
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100) #?
    file_name: Optional[str] = f"{uuid.uuid4()}"
    save_folder: Optional[str] = config.BUF_PATH
    result_matrix_save_folder: Optional[str] = config.BUF_PATH
    files_path: Optional[List[Path]] = None
    frame_number: Optional[int] = 0
    correct_matrix_path: Optional[Path] = None


