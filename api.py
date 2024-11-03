import asyncio
import base64
import logging
import io
import os

from fastapi import FastAPI, Query, BackgroundTasks
from httpx import request
from pydantic import BaseModel
from rich.emoji import NoEmoji
from starlette.responses import StreamingResponse

from src import graphics, logics
from typing import List, Optional
from src import file
from src.file import FitsInfo
from concurrent.futures import ProcessPoolExecutor

from src.graphics.graphics import auto_contrast
from src.logics import write_data_in_file

app = FastAPI()

# Ограничения на количество одновременно выполняемых задач
video_task_semaphore = asyncio.Semaphore(2)  # Одновременно можно обрабатывать 2 задачи по созданию видео
img_task_semaphore = asyncio.Semaphore(3)  # Одновременно можно обрабатывать 3 задачи по созданию видео

# Процессный пул для тяжелых задач
video_executor = ProcessPoolExecutor(max_workers=2)
img_executor = ProcessPoolExecutor(max_workers=3)

class_registry = file.class_registry

running_tasks_name = []
running_tasks = []

@app.get("/tasks")
async def get_tasks():
    # Получаем список активных задач
    active_tasks = [task for task in running_tasks_name]
    return {
        "active_tasks": len(active_tasks),
        "task_status": [{"task": str(task)} for task in active_tasks]
    }


@app.get("/", description="Получить привет")
async def root():
    return {"message": "Hello World"}


# Создаём модель для входных данных
class CreateVideoRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    start_i: Optional[int] = 0
    end_i: Optional[int] = None
    name_file: Optional[str] = "output"
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    mask: Optional[bool] = False
    frame_title: Optional[bool] = False
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
    multiplication_on_correct_matrix: Optional[bool] = True
    Rayleigh: Optional[bool] = False
    result_matrix_safe_folder: Optional[str] = None
    type_diff: Optional[int] = 1
    upper_limit: Optional[float] = 500.
    lower_limit: Optional[float] = None
    logfun: Optional[str] = None
    counts_checks: Optional[int] = 4
    check_frame: List[int] = None
    bins: Optional[int] = 5000
    fps: Optional[int] = 1
    frames_s: Optional[int] = 1
    data_index: Optional[int] = None


# Пример функции, которая выполняет тяжелую операцию по созданию видео
def create_video_logic(request: CreateVideoRequest):
    return logics.create_video(
        names_files=request.files_list,
        new_path=rf"{request.data_path}",
        start_i=request.start_i,
        end_i=request.end_i,
        name_file=request.name_file,
        flag_info=request.flag_info,
        name=request.general_title,
        cut=request.mask,
        names=request.frame_title,
        save_folder=fr"{request.save_folder}",
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
        result_matrix_safe_folder=request.result_matrix_safe_folder,
        type_diff=request.type_diff,
        counts_checks=request.counts_checks,
        check_frame=request.check_frame,
        bins=request.bins,
        fps=request.fps,
        frames_s=request.frames_s,
        data_index=request.data_index,
        multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
        upper_limit=request.upper_limit,
        lower_limit=request.lower_limit
    )



# Создаём POST-эндпоинт
@app.post("/create_video")
async def create_video_endpoint(request: CreateVideoRequest):
    async with video_task_semaphore:  # Ограничиваем количество одновременных задач
        loop = asyncio.get_event_loop()

        task = loop.run_in_executor(video_executor, create_video_logic, request)
        running_tasks_name.append(f"create_video {request}")
        running_tasks.append(task)

        task.add_done_callback(lambda t: running_tasks_name.remove(f"create_video {request}"))
        task.add_done_callback(lambda t: running_tasks.remove(t))

        result = await task

        return result




# Модель запроса
class CreateImageForVideoRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    frame_id: Optional[int] = 0
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    mask: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    frame_title: Optional[bool] = False
    save_folder: Optional[str] = None
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    dark: Optional[bool] = False
    dark_name: Optional[str] = "DARK"
    zip: Optional[bool] = True
    hists: Optional[bool] = True
    remove_single_pixels: Optional[bool] = False
    correct_matrix: Optional[str] = None
    multiplication_on_correct_matrix: Optional[bool] = True
    Rayleigh: Optional[bool] = False
    result_matrix_safe_folder: Optional[str] = None
    type_diff: Optional[int] = 1
    upper_limit: Optional[float] = 500.
    lower_limit: Optional[float] = None
    bins: Optional[int] = 5000
    logfun: Optional[str] = None  # Или замените на нужный тип
    data_index: Optional[int] = None,
    file_name: Optional[str] = "buf"


def create_img_logic(request: CreateImageForVideoRequest):
    logics.create_img_for_video(
        names_files=request.files_list,
        new_path=request.data_path,
        start_i=request.frame_id,
        end_i=request.frame_id + 1,
        flag_info=request.flag_info,
        name=request.general_title,
        cut=request.mask,
        percent_to_trim=request.percent_to_trim,
        names=request.frame_title,
        save_folder=request.save_folder,
        figsize=request.figsize,
        fit_format=class_registry[request.fit_format],
        dark=request.dark,
        dark_name=request.dark_name,
        _zip=request.zip,
        hists=request.hists,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix,
        Rayleigh=request.Rayleigh,
        result_matrix_safe_folder=request.result_matrix_safe_folder,
        type_diff = request.type_diff,
        bins=request.bins,
        counts_checks=1,
        check_frame=None,
        logfun=None,
        data_index=request.data_index,
        file_name=request.file_name,
        multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
        upper_limit=request.upper_limit,
        lower_limit=request.lower_limit
    )

    return  os.path.join(request.save_folder, f'{request.file_name}.png')


# Модель для ответа с изображениями
class ImagesResponse(BaseModel):
    images: List[str]


# Эндпоинт
@app.post("/create_image_for_video")
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



@app.post("/remove/task")
async def remove_task(task_id: str):
    if len(running_tasks_name)>0 and len(running_tasks) > int(task_id):
        running_tasks[int(task_id)].cancel()
        return {"status": f"Task {running_tasks_name[int(task_id)]} has been cancelled"}
    else:
        return {"status": f"Running_tasks: {len(running_tasks)}"}




# Модель запроса
class CreateImageRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    frame_id: Optional[int] = 0
    flag_info: Optional[bool] = False
    general_title: Optional[str] = None
    mask: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    save_folder: Optional[str] = None
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    dark: Optional[bool] = False
    dark_name: Optional[str] = "DARK"
    zip: Optional[bool] = True
    remove_single_pixels: Optional[bool] = False
    correct_matrix: Optional[str] = None
    multiplication_on_correct_matrix: Optional[bool] = True
    Rayleigh: Optional[bool] = False
    result_matrix_safe_folder: Optional[str] = None
    check_frame: Optional[int] = None
    logfun: Optional[str] = None  # Или замените на нужный тип
    data_index: Optional[int] = None,
    file_name: Optional[str] = "buf"



def create_image_logic(request: CreateImageRequest):
    logics.create_image(
        names_files=request.files_list,
        new_path=request.data_path,
        number=request.frame_id,
        flag_info=request.flag_info,
        name=request.general_title,
        cut=request.mask,
        percent_to_trim=request.percent_to_trim,
        save_folder=request.save_folder,
        figsize=request.figsize,
        fit_format=class_registry[request.fit_format],
        dark=request.dark,
        dark_name=request.dark_name,
        _zip=request.zip,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix,
        Rayleigh=request.Rayleigh,
        result_matrix_safe_folder=request.result_matrix_safe_folder,
        logfun=None,
        data_index=request.data_index,
        file_name=request.file_name,
        multiplication_on_correct_matrix=request.multiplication_on_correct_matrix
    )

    return  os.path.join(request.save_folder, f'{request.file_name}.png')


@app.post("/create_img")
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




class CreateHeatmapRequest(BaseModel):
    data_path: str
    files_list: List[str] = []
    start_i: Optional[int] = 0
    end_i: Optional[int] = None
    edges: Optional[int] = 0
    flag_info: Optional[bool] = False
    title: Optional[str] = None
    mask: Optional[bool] = False
    percent_to_trim: Optional[float] = 0.1
    save_folder: Optional[str] = None
    figsize: Optional[tuple] = (1920 / 100, 1080 / 100)
    fit_format: Optional[str] = "FitsInfo"  # Замените тип на нужный, если требуется
    dark: Optional[bool] = False
    dark_name: Optional[str] = "DARK"
    zip: Optional[bool] = True
    remove_single_pixels: Optional[bool] = False
    correct_matrix: Optional[str] = None
    multiplication_on_correct_matrix: Optional[bool] = True
    Rayleigh: Optional[bool] = False
    counts_checks: Optional[int] = 4
    check_frame: Optional[int] = None
    auto_contrast: Optional[bool] = True
    auto_contrast_percentiles: List[int] = [2, 98]
    result_auto_contrast: Optional[bool] = True
    bins: Optional[int] = 500
    cmap: Optional[str] = "viridis"
    logfun: Optional[str] = None  # Или замените на нужный тип
    data_index: Optional[int] = None,
    file_name: Optional[str] = "buf"


def create_heatmap_logic(request: CreateHeatmapRequest):
    logics.create_heatmap(
        names=request.files_list,
        new_path=request.data_path,
        start_file=request.start_i,
        end_file=request.end_i,
        edges=request.edges,
        title=request.title,
        bins=request.bins,
        cmap=request.cmap,
        save_folder=request.save_folder,
        _zip=request.zip,
        counts_checks=request.counts_checks,
        check_frame=request.check_frame,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix,
        multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
        Rayleigh=request.Rayleigh,
        dark=request.dark,
        dark_name=request.dark_name,
        cut=request.mask,
        percent_to_trim=request.percent_to_trim,
        data_index=request.data_index,
        q=request.auto_contrast_percentiles,
        name_file=request.file_name,
        result_auto_contrast=request.result_auto_contrast,
        auto_contrast=request.auto_contrast
    )
    return os.path.join(request.save_folder, f'{request.file_name}.png')


@app.post("/create_heatmap")
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


async def create_video():
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
