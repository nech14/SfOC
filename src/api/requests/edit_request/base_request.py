from typing import List

from pydantic import BaseModel

# Модель для ответа с изображениями
class ImagesResponse(BaseModel):
    images: List[str]

