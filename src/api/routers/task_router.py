from fastapi import APIRouter

from config import rout_root, running_tasks_name, running_tasks
from src.api.api_tags import ApiTags

router = APIRouter(prefix="/task", tags=[ApiTags.Tasks.value])


@router.get(f"{rout_root}/", description="Проверка api")
async def root():
    return {"status": "200"}


@router.get(f"{rout_root}/tasks", tags=[ApiTags.Tasks.value])
async def get_tasks():
    # Получаем список активных задач
    active_tasks = [task for task in running_tasks_name]
    return {
        "active_tasks": len(active_tasks),
        "task_status": [{"task": str(task)} for task in active_tasks]
    }


@router.post(f"{rout_root}/remove/task", tags=[ApiTags.Tasks.value])
async def remove_task(task_id: str):
    if len(running_tasks_name)>0 and len(running_tasks) > int(task_id):
        running_tasks[int(task_id)].cancel()
        return {"status": f"Task {running_tasks_name[int(task_id)]} has been cancelled"}
    else:
        return {"status": f"Running_tasks: {len(running_tasks)}"}