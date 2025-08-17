

import asyncio
import io
import os

from starlette.responses import StreamingResponse

from src.api import database_api, editor_api
from src.api.api_tags import tags, ApiTags
from src.api.logic.logic import get_dark_files_logic, create_video_logic, create_img_logic, create_image_logic, \
    create_heatmap_logic
from src.api.schemas_request.base_request import CreateImageRequest, CreateHeatmapRequest, CreateImageForVideoRequest, GetDarkFilesRequest, CreateVideoRequest
from src import file
from concurrent.futures import ProcessPoolExecutor

from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from src.editor.editor import Editor
from src.logging.logging import setup_logging



setup_logging()
app = FastAPI(
    openapi_tags=[
        {"name": tags[0], "description": "Эндпоинты работы с задачами"},
        {"name": tags[1], "description": "Эндпоинты работы с картинками"},
        {"name": tags[2], "description": "Эндпоинты работы с картинками"},
    ]
)

app.include_router(database_api.router)
app.include_router(editor_api.router)
static_path = os.path.join(os.path.dirname(__file__), "src", "api", "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

editor: Editor|None = None




# Ограничения на количество одновременно выполняемых задач
video_task_semaphore = asyncio.Semaphore(2)  # Одновременно можно обрабатывать 2 задачи по созданию видео
img_task_semaphore = asyncio.Semaphore(3)  # Одновременно можно обрабатывать 3 задачи по созданию видео

# Процессный пул для тяжелых задач
video_executor = ProcessPoolExecutor(max_workers=2)
img_executor = ProcessPoolExecutor(max_workers=3)

class_registry = file.class_registry

running_tasks_name = []
running_tasks = []

rout_root = ""

@app.get(f"{rout_root}/", description="Получить привет")
async def root():
    return {"message": "Hello World"}


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


@app.post(f"{rout_root}/get_dark_files", tags=[ApiTags.Edit.value])
async def get_dark_files(request: GetDarkFilesRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, get_dark_files_logic, request)
        running_tasks_name.append(f"get_dark_files_logic {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"get_dark_files_logic {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()


        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")


# Создаём POST-эндпоинт
@app.post(f"{rout_root}/create_video", tags=[ApiTags.Edit.value])
async def create_video_endpoint(request: CreateVideoRequest):
    async with video_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(video_executor, create_video_logic, request)
        running_tasks_name.append(f"create_video {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_video {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        return FileResponse(
            result,
            media_type="video/mp4",
            filename=os.path.basename(result)
        )


# Эндпоинт
@app.post(f"{rout_root}/create_image_for_video", tags=[ApiTags.Edit.value])
async def create_image_for_video_endpoint(request: CreateImageForVideoRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, create_img_logic, request)
        running_tasks_name.append(f"create_image {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_image {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()


        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")


@app.post(f"{rout_root}/create_img", tags=[ApiTags.Edit.value])
async def create_img(request: CreateImageRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, create_image_logic, request)
        running_tasks_name.append(f"create_image {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_image {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()


        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")






@app.post(f"{rout_root}/create_heatmap", tags=[ApiTags.Edit.value])
async def create_heatmap(request: CreateHeatmapRequest):
    async with video_task_semaphore:
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(video_executor, create_heatmap_logic, request)
        running_tasks_name.append(f"create_heatmap {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_heatmap {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()

        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")


