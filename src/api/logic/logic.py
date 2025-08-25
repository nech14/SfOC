import os
from datetime import datetime
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt, gridspec

from src.api.requests.edit_request.create_heatmap_request import CreateHeatmapRequest
from src.api.requests.edit_request.create_image_for_video_request import CreateImageForVideoRequest
from src.api.requests.edit_request.create_image_request import CreateImageRequest
from src.api.requests.edit_request.create_video_request import CreateVideoRequest
from src.api.requests.edit_request.get_dark_files_request import GetDarkFilesRequest
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.models.recipes_models.image_recipe_model import ImageRecipe
from src.models.recipes_models.video_recipe_model import VideoRecipe
from src.pipeline import orchestrator
from src.utils.common.common import print_vars
from src.utils.common.fits_formats import fits_formats
from src.utils.logics.work_with_dark import get_dark, get_dark_avg, show_darks_frames
from src.utils.file import file


def create_video_image_logic(request: CreateImageForVideoRequest):
    recipe = VideoRecipe.get_recipe_by_request(request)

    print_vars(recipe)
    orchestrator.create_image_for_video(recipe, request.frame_number)

    return  os.path.join(request.save_folder, f'{request.file_name}.png')


def create_video_logic(request: CreateVideoRequest):
    recipe = VideoRecipe.get_recipe_by_request(request)
    return orchestrator.create_video(recipe)

def get_dark_files_logic(request: GetDarkFilesRequest) -> Path:
    if request.files_list is None or len(request.files_list) == 0:
        request.files_list = file.get_name_files(request.data_path)

    fit_format = fits_formats[request.fit_format]

    dark_data= get_dark(
        request.files_list,
        Path(request.data_path),
        request.dark_file_name,
        _zip=request.zipped_file,
        fit_format=fit_format)

    dark_data_flip= get_dark(
        np.flip(request.files_list),
        Path(request.data_path),
        request.dark_file_name,
        _zip=request.zipped_file,
        fit_format=fit_format)
    dark_data_flip = np.flip(dark_data_flip)
    dark_data = [*dark_data, *dark_data_flip]

    save_path = show_darks_frames(
        dark_data,
        save_folder=Path(request.save_folder),
        file_name=request.file_name,
        title=request.title,
        row_f=request.row_f,
        column_f=request.column_f,
        figsize=request.figsize
    )

    return save_path


def get_dark_files_logic_old(request: GetDarkFilesRequest) -> str:
    if request.files_list is None or len(request.files_list) == 0:
        request.files_list = file.get_name_files(request.data_path)

    request.fit_format = fits_formats[request.fit_format]

    datas_start, times_start = get_dark(
        request.files_list,
        request.data_path,
        request.dark_file_name,
        _zip=request.zipped_file,
        fit_format=request.fit_format)

    datas_end, times_end = get_dark(
        np.flip(request.files_list),
        request.data_path,
        request.dark_file_name,
        _zip=request.zipped_file,
        fit_format=request.fit_format)

    datas_end = np.flip(datas_end)
    times_end = np.flip(times_end)

    dark_start = get_dark_avg(
        request.files_list,
        request.data_path,
        dark_name=request.dark_file_name,
        _zip=request.zipped_file,
        fit_format=request.fit_format
    )
    dart_end = get_dark_avg(
        np.flip(request.files_list),
        request.data_path,
        dark_name=request.dark_file_name,
        _zip=request.zipped_file,
        fit_format=request.fit_format
    )

    all_arrays = list(datas_start) + [dark_start.frame] + list(datas_end) + [dart_end.frame]
    vmin = min(arr.min() for arr in all_arrays)
    vmax = max(arr.max() for arr in all_arrays)

    row1_count = len(datas_start)+1
    row2_count = len(datas_end)+1

    fig = plt.figure(figsize=(26, 6))

    # Создаем сетку: 2 строки, кол-во колонок = макс(row1_count, row2_count)
    total_cols = max(row1_count, row2_count) + 1
    gs = gridspec.GridSpec(2, total_cols, figure=fig, width_ratios=[1] * (total_cols - 1) + [0.05])

    im = None

    # Первый ряд
    for i in range(row1_count-1):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(datas_start[i])
        ax.set_title(f"{times_start[i]}")
        ax.invert_yaxis()

    ax = fig.add_subplot(gs[0, row1_count-1])
    ax.imshow(dark_start.frame)
    ax.set_title("AVG_start")
    ax.invert_yaxis()

    for i in range(row2_count-1):
        ax = fig.add_subplot(gs[1, i])
        ax.imshow(datas_end[i])
        ax.set_title(f"{times_end[i]}")
        ax.invert_yaxis()

    ax = fig.add_subplot(gs[1, row2_count-1])
    im = ax.imshow(dart_end.frame)
    ax.set_title("AVG_end")
    ax.invert_yaxis()

    title_date = datetime.fromtimestamp(times_start[0].timestamp()).date()
    fig.suptitle(f"{title_date}")

    # Добавляем colorbar в отдельную колонку
    cax = fig.add_subplot(gs[:, -1])  # охватывает обе строки
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("Интенсивность", rotation=90)

    plt.tight_layout()

    if request.save_folder is None:
        request.save_folder = "buf"

    if not os.path.exists(request.save_folder):
        os.makedirs(request.save_folder)

    if request.file_name is None:
        file_name_buf = request.names_files[request.frame_number]
    else:
        file_name_buf = request.file_name

    result = request.save_folder + f"/{file_name_buf}.png"
    plt.savefig(result, bbox_inches='tight')
    plt.close()

    return result


def create_image_logic(request: CreateImageRequest):
    recipe = ImageRecipe.get_recipe_by_request(request)
    orchestrator.create_image(recipe)

    return  os.path.join(request.save_folder, f'{request.file_name}.png')


def create_heatmap_logic(request: CreateHeatmapRequest):
    recipe = HeatmapRecipe.get_recipe_by_request(request)
    for k, v in vars(recipe).items():
        print(f"{k} = {v}")
    orchestrator.create_heatmap(recipe)

    return os.path.join(request.save_folder, f'{request.file_name}.png')



