from enum import Enum

tags = ["Здачи", "Редактирование", "База данных"]

class ApiTags(Enum):
    Tasks = tags[0]
    Edit = tags[1]
    Database = tags[2]
