from typing import Optional, List

from pydantic import BaseModel


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
