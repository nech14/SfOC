from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel


class CreateHeatmapDbRequest(BaseModel):
    id_night: int
    id_filter: int
    first_frame_number: Optional[int] = 0
    last_frame_number: Optional[int] = None
    edges: Optional[int] = 0
    fit_format: Optional[str] = "FitsInfo"
    zipped_file: Optional[bool] = True
    counts_checks: Optional[int] = 4
    check_frame: Optional[int] = None
    data_index: Optional[int] = None
    title: Optional[str] = None
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    dark: Optional[bool] = False
    remove_single_pixels: Optional[bool] = False
    use_correct_matrix: Optional[bool] = False
    multiplication_on_correct_matrix: Optional[bool] = True
    rayleigh: Optional[bool] = False
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    bins: Optional[int] = 500
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    cmap: Optional[str] = "viridis"
    cmap_under: Optional[str] = None
    file_name: Optional[str] = "buf"
    save_folder: Optional[str] = "buf"


class CreateHeatmapDbInternal(CreateHeatmapDbRequest):
    files_path: Optional[List[Path]] = None
    correct_matrix_path: Optional[Path] = None
