import asyncio
import io
import os
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from starlette.responses import StreamingResponse

from config import rout_root, img_task_semaphore, running_tasks_name, running_tasks, img_executor
from src.api.api_tags import ApiTags
from src.api.requests.edit_db_request.create_image_db_request import CreateImageDbRequest, CreateImageDbInternal

from src.database.database import Session
from src.database.models.models import Background, BackgroundsAll
from src.models.recipes.image_recipe_model import ImageRecipe
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



@router.post(f"{rout_root}/create_img", tags=[ApiTags.EditDatabase.value])
async def create_img(request: CreateImageDbRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, create_image_db_logic, request)
        running_tasks_name.append(f"create_image {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_image {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()


        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")


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