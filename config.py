import asyncio
import os
from concurrent.futures import ProcessPoolExecutor


rout_root = os.getenv("rout_root")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
video_tasks_count = os.getenv("video_tasks_count", 2)
img_tasks_count = os.getenv("img_tasks_count", 3)

# Ограничения на количество одновременно выполняемых задач
video_task_semaphore = asyncio.Semaphore(video_tasks_count)  # Одновременно можно обрабатывать 2 задачи по созданию видео
img_task_semaphore = asyncio.Semaphore(img_tasks_count)  # Одновременно можно обрабатывать 3 задачи по созданию видео

# Процессный пул для тяжелых задач
video_executor = ProcessPoolExecutor(max_workers=video_tasks_count)
img_executor = ProcessPoolExecutor(max_workers=img_tasks_count)

running_tasks_name = []
running_tasks = []


