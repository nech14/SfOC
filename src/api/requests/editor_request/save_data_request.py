from pydantic import BaseModel
from typing import Optional

class SaveDataRequest(BaseModel):
    save_folder: Optional[str] = ""
    name_file: Optional[str] = ""