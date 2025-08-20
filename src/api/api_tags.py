from enum import Enum

tags = ["Здачи", "Редактор", "База данных", "Редактирование", "Редактирование с БД"]

class ApiTags(Enum):
    Tasks = tags[0]
    Editor = tags[1]
    Database = tags[2]
    Edit = tags[3]
    EditDatabase = tags[4]

