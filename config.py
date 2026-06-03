import asyncio
import os
from concurrent.futures import ProcessPoolExecutor

from dotenv import load_dotenv

load_dotenv()

API_IP = os.getenv("api_ip", "0.0.0.0")
API_PORT = int(os.getenv("api_port", 8000))
API_ROOT = os.getenv("api_root", "")
ENABLE_DATABASE_ROUTER = os.getenv("enable_database_router", "True").lower() in ("true", "1", "yes")
ENABLE_EDITOR_ROUTER = os.getenv("enable_editor_router", "True").lower() in ("true", "1", "yes")
ENABLE_EDIT_ROUTER = os.getenv("enable_edit_router", "True").lower() in ("true", "1", "yes")
ENABLE_EDIT_DB_ROUTER = os.getenv("enable_edit_db_router", "True").lower() in ("true", "1", "yes")
BUF_PATH = os.getenv("BUF_PATH", "buf")

DATABASE_IP = os.getenv("database_ip", "127.0.0.1")
DATABASE_PORT = int(os.getenv("database_port", 3306))
DATABASE_USER = os.getenv("database_user", "root")
DATABASE_PASSWORD = os.getenv("database_password", "")
DATABASE_NAME = os.getenv("database_name", "db")
DATABASE_PRINT_SQL_QUERIES = os.getenv("database_print_sql_queries", "True").lower() in ()

if DATABASE_PASSWORD:
    DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_IP}:{DATABASE_PORT}/{DATABASE_NAME}"
else:
    DATABASE_URL = f"mysql+pymysql://root@{DATABASE_IP}:{DATABASE_PORT}/{DATABASE_NAME}"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "True").lower() in ("true", "1", "yes")
LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "True").lower() in ("true", "1", "yes")
LOG_FORMAT = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

ENABLE_TASKS_ROUTER = True
VIDEO_TASKS_COUNT = int(os.getenv("video_tasks_count", 2))
IMG_TASKS_COUNT = int(os.getenv("img_tasks_count", 3))

# Ограничения на количество одновременно выполняемых задач
video_task_semaphore = asyncio.Semaphore(
    VIDEO_TASKS_COUNT
)  # Одновременно можно обрабатывать 2 задачи по созданию видео
img_task_semaphore = asyncio.Semaphore(IMG_TASKS_COUNT)  # Одновременно можно обрабатывать 3 задачи по созданию видео

# Процессный пул для тяжелых задач
video_executor = ProcessPoolExecutor(max_workers=VIDEO_TASKS_COUNT)
img_executor = ProcessPoolExecutor(max_workers=IMG_TASKS_COUNT)

running_tasks_name = []
running_tasks = []
