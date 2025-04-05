
from pydantic import BaseModel
from typing import Optional


class CorrectMatrixRequest(BaseModel):
    correct_matrix: Optional[str] = ""
    multiplication_on_correct_matrix: Optional[bool]
