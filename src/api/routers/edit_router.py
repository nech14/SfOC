import asyncio
import io
import os

from fastapi import APIRouter
from starlette.responses import StreamingResponse, FileResponse

from config import API_ROOT, img_task_semaphore, img_executor, running_tasks_name, running_tasks, video_task_semaphore, \
    video_executor
from src.api.api_tags import ApiTags
from src.api.logic.logic import get_dark_files_logic, create_video_image_logic, create_image_logic, create_heatmap_logic, \
    create_video_logic
from src.api.requests.edit_request.create_heatmap_request import CreateHeatmapRequest
from src.api.requests.edit_request.create_image_for_video_request import CreateImageForVideoRequest
from src.api.requests.edit_request.create_image_request import CreateImageRequest
from src.api.requests.edit_request.create_video_request import CreateVideoRequest
from src.api.requests.edit_request.get_dark_files_request import GetDarkFilesRequest

router = APIRouter(prefix="/edit", tags=[ApiTags.Edit])



@router.post(f"{API_ROOT}/get_dark_files", tags=[ApiTags.Edit])
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



@router.post(f"{API_ROOT}/create_img", tags=[ApiTags.Edit])
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


@router.post(f"{API_ROOT}/create_video", tags=[ApiTags.Edit])
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


@router.post(f"{API_ROOT}/create_image_for_video", tags=[ApiTags.Edit])
async def create_image_for_video_endpoint(request: CreateImageForVideoRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, create_video_image_logic, request)
        running_tasks_name.append(f"create_image {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_image {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()


        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")




@router.post(f"{API_ROOT}/create_heatmap", tags=[ApiTags.Edit])
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
