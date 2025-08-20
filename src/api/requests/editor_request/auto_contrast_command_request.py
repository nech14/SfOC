from pydantic import BaseModel
from typing import List

class AutoContrastCommandRequest(BaseModel):
    auto_contrast_percentiles: List[int] = [2, 98]