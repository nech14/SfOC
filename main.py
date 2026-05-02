

import os
import uvicorn
import config
from src.api.routers import editor_router, database_router, edit_router, edit_db_router, task_router
from src.api.api_tags import ApiTags, ApiTagsDescription
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from src.utils.common.fits_formats import fits_formats
from src.utils.editor.editor import Editor

if __name__ == "__main__":
    app = FastAPI(
        openapi_tags=[
            {"name": ApiTags.Tasks, "description": ApiTagsDescription.Tasks},
            {"name": ApiTags.Edit, "description": ApiTagsDescription.Edit},
            {"name": ApiTags.EditDatabase, "description": ApiTagsDescription.EditDatabase},
            {"name": ApiTags.Editor, "description": ApiTagsDescription.Editor},
            {"name": ApiTags.Database, "description": ApiTagsDescription.Database},
        ]
    )

    routers = {
        "tasks": (config.ENABLE_TASKS_ROUTER, task_router.router),
        "database": (config.ENABLE_DATABASE_ROUTER, database_router.router),
        "editor": (config.ENABLE_EDITOR_ROUTER, editor_router.router),
        "edit": (config.ENABLE_EDIT_ROUTER, edit_router.router),
        "edit_db": (config.ENABLE_EDIT_DB_ROUTER, edit_db_router.router),
    }

    for name, (enabled, router) in routers.items():
        print(f"{name}: enabled={enabled}")
        if enabled:
            app.include_router(router)

    static_path = os.path.join(os.path.dirname(__file__), "src", "api", "static")
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    editor: Editor | None = None

    class_registry = fits_formats

    uvicorn.run(app, host=config.API_IP, port=config.API_PORT)
