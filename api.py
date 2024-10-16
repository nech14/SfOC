import asyncio
import base64
import logging
import io
import os

from fastapi import FastAPI, Query, BackgroundTasks
from pydantic import BaseModel
from rich.emoji import NoEmoji
from starlette.responses import StreamingResponse

from src import graphics, logics
from typing import List, Optional
from src import file
from src.file import FitsInfo
from concurrent.futures import ProcessPoolExecutor

from src.logics import write_data_in_file

app = FastAPI()

# Ограничения на количество одновременно выполняемых задач
video_task_semaphore = asyncio.Semaphore(2)  # Одновременно можно обрабатывать 2 задачи по созданию видео
img_task_semaphore = asyncio.Semaphore(3)  # Одновременно можно обрабатывать 3 задачи по созданию видео

# Процессный пул для тяжелых задач
video_executor = ProcessPoolExecutor(max_workers=2)
img_executor = ProcessPoolExecutor(max_workers=3)

class_registry = file.class_registry


@app.get("/", description="Получить привет")
async def root():
    return {"message": "Hello World"}


@app.get("/items/")
async def read_items(
    q: str = Query(default="default_value", description="Параметр запроса", example="example_value"),
    limit: int = Query(default=10, description="Лимит на количество результатов", example=5)
):
    return {"q": q, "limit": limit}

# Модель для JSON с примером
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop",
                "description": "A gaming laptop",
                "price": 1500.99,
                "tax": 0.2
            }
        }

# Эндпоинт для обработки JSON
@app.post("/itemss/")
async def create_item(item: Item):
    return {"message": "Item created", "item": item}




# Создаём модель для входных данных
class CreateVideoRequest(BaseModel):
    names_files: List[str]|None = None
    new_path: str
    start_i: Optional[int] = 6
    end_i: Optional[int] = None
    name_file: Optional[str] = "output"
    flag_info: Optional[bool] = False
    name: Optional[str] = None
    cut: Optional[bool] = False
    names: Optional[bool] = False
    save_folder: Optional[str] = ""
    save_folder_video: Optional[str] = None
    save_img: Optional[bool] = False
    name_img_folder: Optional[str] = "img_for_video"
    name_video_folder: Optional[str] = "video"
    dark: Optional[bool] = False
    dark_name: Optional[str] = "DARK"
    fit_format: Optional[str] = "FitsInfo"
    zip: Optional[bool] = True
    hists: Optional[bool] = False
    remove_single_pixels: Optional[bool] = False
    correct_matrix: Optional[str] = None
    Rayleigh: Optional[bool] = False
    logfun: Optional[str] = None
    counts_checks: Optional[int] = 4
    check_frame: List[int]|None = None
    bins: Optional[int] = 5000
    fps: Optional[int] = 1
    frames_s: Optional[int] = 1
    data_index: List[int]|None = None


# Пример функции, которая выполняет тяжелую операцию по созданию видео
def create_video_logic(request: CreateVideoRequest):
    return logics.create_video(
        names_files=request.names_files,
        new_path=request.new_path,
        start_i=request.start_i,
        end_i=request.end_i,
        name_file=request.name_file,
        flag_info=request.flag_info,
        name=request.name,
        cut=request.cut,
        names=request.names,
        save_folder=request.save_folder,
        save_folder_video=request.save_folder_video,
        save_img=request.save_img,
        name_img_folder=request.name_img_folder,
        name_video_folder=request.name_video_folder,
        dark=request.dark,
        dark_name=request.dark_name,
        fit_format=class_registry[request.fit_format],
        _zip=request.zip,
        hists=request.hists,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix,
        Rayleigh=request.Rayleigh,
        counts_checks=request.counts_checks,
        check_frame=request.check_frame,
        bins=request.bins,
        fps=request.fps,
        frames_s=request.frames_s,
        data_index=request.data_index
    )

# Создаём POST-эндпоинт
@app.post("/create_video/")
async def create_video_endpoint(request: CreateVideoRequest):
    async with video_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()
        # Передаем функцию, которая не зависит от несериализуемых объектов
        result = await loop.run_in_executor(video_executor, create_video_logic, request)
        return result






# Модель запроса
class CreateImageForVideoRequest(BaseModel):
    names_files: List[str]|None = None
    new_path: str
    frame_id: Optional[int] = 0
    flag_info: Optional[bool] = False
    name: Optional[str] = None
    cut: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    names: Optional[bool] = False
    save_folder: Optional[str] = None
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    dark: Optional[bool] = False
    dark_name: Optional[str] = "DARK"
    n: Optional[int] = 10000
    zip: Optional[bool] = True
    hists: Optional[bool] = True
    remove_single_pixels: Optional[bool] = False
    correct_matrix: Optional[str] = None  # Замените тип на нужный
    Rayleigh: Optional[bool] = False
    bins: Optional[int] = 5000
    counts_checks: Optional[int] = 4
    check_frame: Optional[int] = None
    logfun: Optional[str] = None  # Или замените на нужный тип
    data_index: Optional[int] = None


def create_img_logic(request: CreateImageForVideoRequest):
    logics.create_img_for_video(
        names_files=request.names_files,
        new_path=request.new_path,
        start_i=request.frame_id,
        end_i=request.frame_id + 1,
        flag_info=request.flag_info,
        name=request.name,
        cut=request.cut,
        percent_to_trim=request.percent_to_trim,
        names=request.names,
        save_folder=request.save_folder,
        figsize=request.figsize,
        fit_format=class_registry[request.fit_format],
        dark=request.dark,
        dark_name=request.dark_name,
        n=request.n,
        _zip=request.zip,
        hists=request.hists,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix,
        Rayleigh=request.Rayleigh,
        bins=request.bins,
        counts_checks=request.counts_checks,
        check_frame=request.check_frame,
        logfun=None,
        data_index=request.data_index)

    return  os.path.join(request.save_folder, f'{request.frame_id}.png')


# Модель для ответа с изображениями
class ImagesResponse(BaseModel):
    images: List[str]


# Эндпоинт
@app.post("/create_image_for_video/")
async def create_image_for_video_endpoint(request: CreateImageForVideoRequest):

    async with img_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()
        # Передаем функцию, которая не зависит от несериализуемых объектов
        result = await loop.run_in_executor(img_executor, create_img_logic, request)


        # Читаем файл изображения в бинарном режиме
        with open(result, "rb") as image_file:
            img_data = image_file.read()

        return StreamingResponse(io.BytesIO(img_data), media_type="image/png")





async def get_diff():
    pass

async def create_video():
    pass

async def create_img_for_video():
    pass

async def get_hist_p():
    pass

async def slic_dbscan():
    pass


async def get_fits_format():
    pass


async def get_logging_fun():
    pass


async def canny_frame():
    pass
