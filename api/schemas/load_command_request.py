from pydantic import BaseModel
from typing import Optional, List

class LoadCommandRequest(BaseModel):
    root_path: Optional[str] = ""
    names_files: Optional[List[str]] = None
    start_file: Optional[int] = 0
    end_file: Optional[int] = None
    _zip: Optional[bool] = False
    fit_format: Optional[str] = None
    data_index: Optional[int] = None