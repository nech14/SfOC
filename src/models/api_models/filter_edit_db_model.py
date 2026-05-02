from pydantic import BaseModel


class FilterEditDbModel(BaseModel):
    id: int
    path: str
    filename: str