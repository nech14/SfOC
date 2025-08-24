from pydantic import BaseModel


class FrameEditDbModel(BaseModel):
    frameId: int
    id_night: int
    framePath: str
    camera: str
    filter: str
    matrixFolder: str
    matrixName: str
