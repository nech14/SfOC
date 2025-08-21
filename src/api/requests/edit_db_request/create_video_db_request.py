from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel


class CreateVideoDbRequest(BaseModel):
    id_night: int
    id_filter: int
    first_frame_number: Optional[int] = 0
    last_frame_number: Optional[int] = None
    fit_format: Optional[str] = "FitsInfo"
    zipped_file: Optional[bool] = True
    flag_info: Optional[bool] = False
    cut: Optional[bool] = False
    dark: Optional[bool] = False
    remove_single_pixels: Optional[bool] = False
    use_correct_matrix: Optional[bool] = False
    multiplication_on_correct_matrix: Optional[bool] = True
    rayleigh: Optional[bool] = False
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    type_diff: Optional[int] = 1
    upper_limit: Optional[float] = 500.
    lower_limit: Optional[float] = None
    hist: Optional[bool] = False
    bins: Optional[int] = 100
    counts_checks: Optional[int] = 4
    check_frame: List[int] = None
    fps: Optional[float] = 1
    frames_s: Optional[int] = 1
    data_index: Optional[int] = None
    general_title: Optional[str] = None
    frame_title: Optional[bool] = False
    name_file: Optional[str] = "output"
    name_img_folder: Optional[str] = "img_for_video"
    name_video_folder: Optional[str] = "video"
    save_folder: Optional[str] = ""
    save_folder_video: Optional[str] = None
    result_matrix_save_folder: Optional[str] = None
    save_img: Optional[bool] = False



class CreateVideoDbInternal(CreateVideoDbRequest):
    files_path: Optional[List[Path]] = None
    correct_matrix_path: Optional[Path] = None

