

import os
from config import rout_root, running_tasks_name, running_tasks
from src.api.routers import editor_router, database_router, edit_router
from src.api.api_tags import tags, ApiTags
from src import file
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from src.editor.editor import Editor
from src.logging.logging import setup_logging

setup_logging()
app = FastAPI(
    openapi_tags=[
        {"name": tags[0], "description": "Эндпоинты работы с задачами"},
        {"name": tags[3], "description": "Эндпоинты работы с картинками"},
        {"name": tags[1], "description": "Эндпоинты работы с картинками"},
        {"name": tags[2], "description": "Эндпоинты работы с картинками"},
    ]
)

app.include_router(database_router.router)
app.include_router(editor_router.router)
app.include_router(edit_router.router)
static_path = os.path.join(os.path.dirname(__file__), "src", "api", "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

editor: Editor|None = None

class_registry = file.class_registry


@app.get(f"{rout_root}/", description="Проверка api")
async def root():
    return {"status": "200"}


@app.get(f"{rout_root}/tasks", tags=[ApiTags.Tasks.value])
async def get_tasks():
    # Получаем список активных задач
    active_tasks = [task for task in running_tasks_name]
    return {
        "active_tasks": len(active_tasks),
        "task_status": [{"task": str(task)} for task in active_tasks]
    }


@app.post(f"{rout_root}/remove/task", tags=[ApiTags.Tasks.value])
async def remove_task(task_id: str):
    if len(running_tasks_name)>0 and len(running_tasks) > int(task_id):
        running_tasks[int(task_id)].cancel()
        return {"status": f"Task {running_tasks_name[int(task_id)]} has been cancelled"}
    else:
        return {"status": f"Running_tasks: {len(running_tasks)}"}

