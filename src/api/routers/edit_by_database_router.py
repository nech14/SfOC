import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy import text

from config import rout_root, img_task_semaphore, running_tasks_name, running_tasks, img_executor
from src.api.api_tags import ApiTags

from src.database.database import Session

router = APIRouter(prefix="/editDB", tags=[ApiTags.EditDatabase.value])

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

def get_frame_by_id(frame_id: int):
    db = Session()
    try:
        query = text("""
            SELECT 
                frames.id as frameId, 
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
        return result
    finally:
        db.close()


@router.get(f"{rout_root}/create_img_by_db/{{frame_id}}", tags=[ApiTags.EditDatabase.value])
async def create_img_by_db(frame_id: int):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(img_executor, get_frame_by_id, frame_id)
        running_tasks_name.append(f"get frame {frame_id}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"get frame {frame_id}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task


        return result