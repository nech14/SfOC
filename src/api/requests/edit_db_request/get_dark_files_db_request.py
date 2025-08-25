
from typing import Optional, Tuple, List
from pydantic import BaseModel


class GetDarkFilesDbRequest(BaseModel):
    id_night: int
    id_filter: int
    zipped_file: Optional[bool] = True
    fit_format: Optional[str] = "FitsInfo"
    save_folder: Optional[str] = "buf"
    file_name: Optional[str] = 'buf'
    title: Optional[str] = 'dark'
    row_f: Optional[int] = None
    column_f: Optional[int] = None
    figsize: Tuple[float, float] = (12, 12)
