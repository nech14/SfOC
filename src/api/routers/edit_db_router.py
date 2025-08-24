import asyncio
import io
import os

from fastapi import APIRouter
from starlette.responses import StreamingResponse, FileResponse

from config import rout_root, img_task_semaphore, running_tasks_name, running_tasks, img_executor, video_task_semaphore, \
    video_executor
from src.api.api_tags import ApiTags
from src.api.base_api import create_heatmap_logic
from src.api.logic.edit_db_logic import create_video_image_db_logic, create_video_db_logic, create_image_db_logic, get_frame_by_id
from src.api.requests.edit_db_request.create_heatmap_db_request import CreateHeatmapDbRequest
from src.api.requests.edit_db_request.create_image_db_request import CreateImageDbRequest
from src.api.requests.edit_db_request.create_image_for_video_db_request import CreateImageForVideoDbRequest
from src.api.requests.edit_db_request.create_video_db_request import CreateVideoDbRequest
from src.models.api_models.frame_edit_db_model import FrameEditDbModel

router = APIRouter(prefix="/editDB", tags=[ApiTags.EditDatabase.value])


@router.get(
    f"{rout_root}/create_img_by_db/{{frame_id}}",
    tags=[ApiTags.EditDatabase.value],
    response_model=FrameEditDbModel
)
async def get_img_data_by_db(frame_id: int) -> FrameEditDbModel | None:

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, get_frame_by_id, frame_id)
        running_tasks_name.append(f"get frame {frame_id}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"get frame {frame_id}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task


        return result



@router.post(f"{rout_root}/create_img_db", tags=[ApiTags.EditDatabase.value])
async def create_img(request: CreateImageDbRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, create_image_db_logic, request)
        running_tasks_name.append(f"create_image_db {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_image_db {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()


        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")


# Эндпоинт
@router.post(f"{rout_root}/create_image_for_video_db", tags=[ApiTags.EditDatabase.value])
async def create_image_for_video_endpoint(request: CreateImageForVideoDbRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, create_video_image_db_logic, request)
        running_tasks_name.append(f"create_image_db {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_image_db {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()


        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")


@router.post(f"{rout_root}/create_video_db", tags=[ApiTags.EditDatabase.value])
async def create_video_endpoint(request: CreateVideoDbRequest):
    async with video_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(video_executor, create_video_db_logic, request)
        running_tasks_name.append(f"create_video_db {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_video_db {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        return FileResponse(
            result,
            media_type="video/mp4",
            filename=os.path.basename(result)
        )


@router.post(f"{rout_root}/create_heatmap_db", tags=[ApiTags.Edit.value])
async def create_heatmap(request: CreateHeatmapDbRequest):
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



