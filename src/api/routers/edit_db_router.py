import asyncio
import io
import os
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from starlette.responses import StreamingResponse, FileResponse

from config import rout_root, img_task_semaphore, running_tasks_name, running_tasks, img_executor, video_task_semaphore, \
    video_executor
from src.api.api_tags import ApiTags
from src.api.requests.edit_db_request.create_image_db_request import CreateImageDbRequest, CreateImageDbInternal
from src.api.requests.edit_db_request.create_image_for_video_db_request import CreateImageForVideoDbRequest, \
    CreateImageForVideoDbInternal
from src.api.requests.edit_db_request.create_video_db_request import CreateVideoDbRequest, CreateVideoDbInternal
from src.api.requests.edit_request.create_image_for_video_request import CreateImageForVideoRequest

from src.database.database import Session
from src.database.models.models import Background, BackgroundsAll, Frames
from src.models.recipes.image_recipe_model import ImageRecipe
from src.models.recipes.video_recipe_model import VideoRecipe
from src.pipeline import orchestrator

router = APIRouter(prefix="/editDB", tags=[ApiTags.EditDatabase.value])

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


class FrameModel(BaseModel):
    frameId: int
    id_night: int
    framePath: str
    camera: str
    filter: str
    matrixFolder: str
    matrixName: str


class FilterModel(BaseModel):
    id: int
    path: str
    filename: str


def get_frame_by_id(frame_id: int) -> FrameModel:
    db = Session()
    try:
        query = text("""
            SELECT 
                frames.id as frameId, 
                frames.id_night as id_night,
                frames.dest as framePath, 
                camera.name as camera, 
                filters.name as filter, 
                paths.ucf as matrixFolder, 
                filters.ucf as matrixName
            FROM frames
            INNER JOIN filters ON frames.id_filtr = filters.id
            INNER JOIN camera ON filters.id_camera = camera.id
            INNER JOIN paths ON filters.id_camera = paths.id_camera
            WHERE frames.id = :frame_id
        """)
        result = db.execute(query, {"frame_id": frame_id}).mappings().all()
        return result[0] if result else None
    finally:
        db.close()


def get_filter_matrix_by_id(filter_id: int) -> FilterModel:
    db = Session()
    try:
        query = text("""
            SELECT 
                filters.id,
                paths.ucf as "path",
                filters.ucf as "filename" 
            FROM filters 
            INNER JOIN paths ON paths.id_camera = filters.id_camera 
            WHERE filters.id = :filter_id;
        """)
        result = db.execute(query, {"filter_id": filter_id}).mappings().all()
        return result[0] if result else None
    finally:
        db.close()


@router.get(
    f"{rout_root}/create_img_by_db/{{frame_id}}",
    tags=[ApiTags.EditDatabase.value],
    response_model=FrameModel
)
async def get_img_data_by_db(frame_id: int) -> FrameModel | None:

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


# Пример функции, которая выполняет тяжелую операцию по созданию видео
def create_video_db_logic(request: CreateVideoDbRequest):
    frames = get_frames_by_night_filter(request.id_night, request.id_filter)
    frames_path = [frame.dest for frame in frames]
    filter_model = get_filter_matrix_by_id(request.id_filter)
    correct_matrix_path = Path(filter_model.path, filter_model.filename)
    req = CreateVideoDbInternal(**request.model_dump())
    req.files_path = frames_path
    req.correct_matrix_path = correct_matrix_path

    recipe = VideoRecipe.get_recipe_by_request(req)
    if req.dark:
        recipe.dark_file_path = [path.dest for path in get_dark_frames(req.id_night)]


    return orchestrator.create_video(recipe)




def create_video_image_db_logic(request: CreateImageForVideoDbRequest):
    frames = get_frames_by_night_filter(request.id_night, request.id_filter)
    frames_path = [frame.dest for frame in frames]
    filter_model = get_filter_matrix_by_id(request.id_filter)
    correct_matrix_path = Path(filter_model.path, filter_model.filename)
    req = CreateImageForVideoDbInternal(**request.model_dump())
    req.files_path = frames_path
    req.correct_matrix_path = correct_matrix_path

    recipe = VideoRecipe.get_recipe_by_request(req)
    if req.dark:
        recipe.dark_file_path = [path.dest for path in get_dark_frames(req.id_night)]

    for k, v in vars(recipe).items():
        print(f"{k} = {v}")
    orchestrator.create_image_for_video(recipe, req.frame_number)


    return  os.path.join(request.save_folder, f'{request.file_name}.png')


def create_image_db_logic(request: CreateImageDbRequest):

    frameModel = get_frame_by_id(request.frameId)
    req = CreateImageDbInternal(**request.model_dump())
    req.files_path = [Path(frameModel.framePath)]
    req.frame_number = 0
    req.correct_matrix_path = Path(frameModel.matrixFolder, frameModel.matrixName)

    recipe = ImageRecipe.get_recipe_by_request(req)
    if req.dark:
        recipe.dark_file_path = [path.dest for path in get_dark_frames(frameModel.id_night)]

    for k, v in vars(recipe).items():
        print(f"{k} = {v}")
    orchestrator.create_image(recipe)

    return os.path.join(req.save_folder, f'{req.file_name}.png')


def get_dark_frames(id_night: int) -> list[BackgroundsAll]:
    db = Session()
    try:
        return db.query(BackgroundsAll).filter(BackgroundsAll.id_night == id_night).all()
    finally:
        db.close()


def get_frames_by_night_filter(id_night: int, id_filter: int) -> list[Frames]:
    db = Session()
    try:
        return db.query(Frames).filter(Frames.id_night == id_night and Frames.id_filtr == id_filter).all()
    finally:
        db.close()
