from enum import StrEnum

tags = ["Задачи", "Редактор", "База данных", "Редактирование", "Редактирование с БД"]

tags_description = [
    "Эндпоинты работы с задачами",
    "Эндпоинты работы с редактором",
    "Эндпоинты работы с базой данных",
    "Эндпоинты работы с картинками",
    "Эндпоинты работы с картинками с БД"
]


class ApiTags(StrEnum):
    Tasks = tags[0]
    Editor = tags[1]
    Database = tags[2]
    Edit = tags[3]
    EditDatabase = tags[4]


class ApiTagsDescription(StrEnum):
    Tasks = tags_description[0]
    Editor = tags_description[1]
    Database = tags_description[2]
    Edit = tags_description[3]
    EditDatabase = tags_description[4]
