from typing import Optional, List, Tuple

from pydantic import BaseModel


class GetDarkFilesRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    dark_file_name: Optional[str] = "DARK"
    zipped_file: Optional[bool] = True
    fit_format: Optional[str] = "FitsInfo"
    save_folder: Optional[str] = "buf"
    file_name: Optional[str] = 'buf'
    title: Optional[str] = 'dark'
    row_f: Optional[int] = None
    column_f: Optional[int] = None
    figsize: Tuple[float, float] = (12, 12)