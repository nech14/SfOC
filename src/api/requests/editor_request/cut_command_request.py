
from pydantic import BaseModel
from typing import Optional

class CutCommandRequest(BaseModel):
    percent_to_trim: Optional[float] = 0.1