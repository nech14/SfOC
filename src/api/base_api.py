import asyncio
import io
import os

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from src import logics
from src import file
from concurrent.futures import ProcessPoolExecutor

from src.api.requests.edit_request.create_heatmap_request import CreateHeatmapRequest
from src.api.requests.edit_request.create_image_for_video_request import CreateImageForVideoRequest
from src.api.requests.edit_request.create_image_request import CreateImageRequest
from src.api.requests.edit_request.create_video_request import CreateVideoRequest

router = APIRouter()

# Ограничения на количество одновременно выполняемых задач
video_task_semaphore = asyncio.Semaphore(2)  # Одновременно можно обрабатывать 2 задачи по созданию видео
img_task_semaphore = asyncio.Semaphore(3)  # Одновременно можно обрабатывать 3 задачи по созданию видео

# Процессный пул для тяжелых задач
video_executor = ProcessPoolExecutor(max_workers=2)
img_executor = ProcessPoolExecutor(max_workers=3)

class_registry = file.class_registry

running_tasks_name = []
running_tasks = []

rout_root = ""

@router.get(f"{rout_root}/tasks")
async def get_tasks():
    # Получаем список активных задач
    active_tasks = [task for task in running_tasks_name]
    return {
        "active_tasks": len(active_tasks),
        "task_status": [{"task": str(task)} for task in active_tasks]
    }


@router.get(f"{rout_root}/", description="Получить привет")
async def root():
    return {"message": "Hello World"}




# Пример функции, которая выполняет тяжелую операцию по созданию видео
def create_video_logic(request: CreateVideoRequest):
    return logics.create_video(
        names_files=request.files_list,
        new_path=rf"{request.data_path}",
        start_i=request.first_frame_number,
        end_i=request.last_frame_number,
        name_file=request.name_file,
        flag_info=request.flag_info,
        name=request.general_title,
        cut=request.cut,
        names=request.frame_title,
        save_folder=fr"{request.save_folder}",
        save_folder_video=request.save_folder_video,
        save_img=request.save_img,
        name_img_folder=request.name_img_folder,
        name_video_folder=request.name_video_folder,
        dark=request.dark,
        dark_name=request.dark_file_name,
        fit_format=class_registry[request.fit_format],
        _zip=request.zipped_file,
        hists=request.hist,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix_path,
        Rayleigh=request.rayleigh,
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
        lower_limit=request.lower_limit,
        auto_contrast = request.auto_contrast,
        auto_contrast_percentiles = request.auto_contrast_percentiles
    )



# Создаём POST-эндпоинт
@router.post(f"{rout_root}/create_video")
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





def create_img_logic(request: CreateImageForVideoRequest):
    logics.create_img_for_video(
        names_files=request.files_list,
        root_path=request.data_path,
        first_frame_number=request.frame_number,
        last_frame_number=request.frame_number + 1,
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
        hists=request.hist,
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
        lower_limit=request.lower_limit,
        auto_contrast = request.auto_contrast,
        auto_contrast_percentiles = request.auto_contrast_percentiles
    )

    return  os.path.join(request.save_folder, f'{request.file_name}.png')



# Эндпоинт
@router.post(f"{rout_root}/create_image_for_video")
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



@router.post(f"{rout_root}/remove/task")
async def remove_task(task_id: str):
    if len(running_tasks_name)>0 and len(running_tasks) > int(task_id):
        running_tasks[int(task_id)].cancel()
        return {"status": f"Task {running_tasks_name[int(task_id)]} has been cancelled"}
    else:
        return {"status": f"Running_tasks: {len(running_tasks)}"}





def create_image_logic(request: CreateImageRequest):
    logics.create_image(
        names_files=request.files_list,
        root_path=request.data_path,
        number=request.frame_number,
        flag_info=request.flag_info,
        name=request.general_title,
        cut=request.cut,
        percent_to_trim=request.percent_to_trim,
        save_folder=request.save_folder,
        figsize=request.figsize,
        fit_format=class_registry[request.fit_format],
        dark=request.dark,
        dark_name=request.dark_file_name,
        _zip=request.zipped_file,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix_path,
        Rayleigh=request.rayleigh,
        result_matrix_safe_folder=request.result_matrix_save_folder,
        logfun=None,
        data_index=request.data_index,
        file_name=request.file_name,
        multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
        auto_contrast = request.auto_contrast,
        auto_contrast_percentiles = request.auto_contrast_percentiles
    )

    return  os.path.join(request.save_folder, f'{request.file_name}.png')


@router.post(f"{rout_root}/create_img")
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




def create_heatmap_logic(request: CreateHeatmapRequest):
    logics.create_heatmap(
        names=request.files_list,
        new_path=request.data_path,
        start_file=request.first_frame_number,
        end_file=request.last_frame_number,
        edges=request.edges,
        title=request.title,
        bins=request.bins,
        cmap=request.cmap,
        save_folder=request.save_folder,
        _zip=request.zipped_file,
        counts_checks=request.counts_checks,
        check_frame=request.check_frame,
        remove_single_pixels=request.remove_single_pixels,
        correct_matrix=request.correct_matrix_path,
        multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
        Rayleigh=request.rayleigh,
        dark=request.dark,
        dark_name=request.dark_file_name,
        cut=request.cut,
        percent_to_trim=request.percent_to_trim,
        data_index=request.data_index,
        q=request.auto_contrast_percentiles,
        name_file=request.file_name,
        result_auto_contrast=request.result_auto_contrast,
        auto_contrast=request.auto_contrast
    )
    return os.path.join(request.save_folder, f'{request.file_name}.png')


@router.post(f"{rout_root}/create_heatmap")
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

