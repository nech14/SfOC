

import os

import uvicorn

import config
from src.api.routers import editor_router, database_router, edit_router, edit_db_router, task_router
from src.api.api_tags import tags
from src import file
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from src.editor.editor import Editor
from src.logging.logging import setup_logging


if __name__ == "__main__":
    setup_logging()
    app = FastAPI(
        openapi_tags=[
            {"name": tags[0], "description": "Эндпоинты работы с задачами"},
            {"name": tags[3], "description": "Эндпоинты работы с картинками"},
            {"name": tags[4], "description": "Эндпоинты работы с картинками"},
            {"name": tags[1], "description": "Эндпоинты работы с картинками"},
            {"name": tags[2], "description": "Эндпоинты работы с картинками"},
        ]
    )

    app.include_router(task_router.router)
    app.include_router(database_router.router)
    app.include_router(editor_router.router)
    app.include_router(edit_router.router)
    app.include_router(edit_db_router.router)
    static_path = os.path.join(os.path.dirname(__file__), "src", "api", "static")
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    editor: Editor | None = None

    class_registry = file.class_registry

    uvicorn.run(app, host=config.ip, port=config.port)
