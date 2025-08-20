
from pydantic import BaseModel
from typing import List, Optional, Any


class DarkCommandRequest(BaseModel):
    names: List[str] = []
    root_path: Optional[str] = ""
    file_name: Optional[str] = "DARK"
    _zip: Optional[bool] = False
    fit_format: Optional[str] = None