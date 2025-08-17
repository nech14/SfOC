
from typing import Optional, Tuple
from pydantic import BaseModel


class SaveImgRequest(BaseModel):
    save_folder: Optional[str] = ""
    title: Optional[str] = None
    file_name: Optional[str] = None
    figsize: Optional[Tuple[float, float]] = (19.2, 10.8)
    dpi: Optional[int] = 100
    cmap: Optional[str] = "gray"
    axis: Optional[str] = "off"
    bbox_inches: Optional[str] = 'tight'
