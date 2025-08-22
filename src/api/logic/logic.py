import os
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt, gridspec

from src.api.base_api import class_registry
from src.api.requests.edit_request.create_heatmap_request import CreateHeatmapRequest
from src.api.requests.edit_request.create_image_for_video_request import CreateImageForVideoRequest
from src.api.requests.edit_request.create_image_request import CreateImageRequest
from src.api.requests.edit_request.create_video_request import CreateVideoRequest
from src.api.requests.edit_request.get_dark_files_request import GetDarkFilesRequest
from src.models.recipes_models.image_recipe_model import ImageRecipe
from src.models.recipes_models.video_recipe_model import VideoRecipe
from src.pipeline import orchestrator
from src.pipeline.utils.helpers import get_dark, get_dark_avg
from src.utils.file import file
from src.utils.logics import old_logicks


def create_img_logic(request: CreateImageForVideoRequest):
    # logics.create_img_for_video(
    #     names_files=request.files_list,
    #     root_path=request.data_path,
    #     first_frame_number=request.frame_number,
    #     last_frame_number=request.frame_number + 1,
    #     flag_info=request.flag_info,
    #     name=request.general_title,
    #     cut=request.cut,
    #     percent_to_trim=request.percent_to_trim,
    #     names=request.frame_title,
    #     save_folder=request.save_folder,
    #     figsize=request.figsize,
    #     fit_format=class_registry[request.fit_format],
    #     dark=request.dark,
    #     dark_name=request.dark_name,
    #     _zip=request.zip,
    #     hists=request.hist,
    #     remove_single_pixels=request.remove_single_pixels,
    #     correct_matrix=request.correct_matrix,
    #     Rayleigh=request.Rayleigh,
    #     result_matrix_safe_folder=request.result_matrix_safe_folder,
    #     type_diff = request.type_diff,
    #     bins=request.bins,
    #     counts_checks=1,
    #     check_frame=None,
    #     logfun=None,
    #     data_index=request.data_index,
    #     file_name=request.file_name,
    #     multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
    #     upper_limit=request.upper_limit,
    #     lower_limit=request.lower_limit,
    #     auto_contrast = request.auto_contrast,
    #     auto_contrast_percentiles = request.auto_contrast_percentiles
    # )

    recipe = VideoRecipe.get_recipe_by_request(request)
    # for k, v in vars(recipe).items():
    #     print(f"{k} = {v}")
    orchestrator.create_image_for_video(recipe, request.frame_number)


    return  os.path.join(request.save_folder, f'{request.file_name}.png')



def create_video_logic(request: CreateVideoRequest):
    #  logics.create_video(
    #     names_files=request.files_list,
    #     new_path=rf"{request.data_path}",
    #     start_i=request.first_frame_number,
    #     end_i=request.last_frame_number,
    #     name_file=request.name_file,
    #     flag_info=request.flag_info,
    #     name=request.general_title,
    #     cut=request.cut,
    #     names=request.frame_title,
    #     save_folder=fr"{request.save_folder}",
    #     save_folder_video=request.save_folder_video,
    #     save_img=request.save_img,
    #     name_img_folder=request.name_img_folder,
    #     name_video_folder=request.name_video_folder,
    #     dark=request.dark,
    #     dark_name=request.dark_file_name,
    #     fit_format=class_registry[request.fit_format],
    #     _zip=request.zipped_file,
    #     hists=request.hist,
    #     remove_single_pixels=request.remove_single_pixels,
    #     correct_matrix=request.correct_matrix_path,
    #     Rayleigh=request.rayleigh,
    #     result_matrix_safe_folder=request.result_matrix_safe_folder,
    #     type_diff=request.type_diff,
    #     counts_checks=request.counts_checks,
    #     check_frame=request.check_frame,
    #     bins=request.bins,
    #     fps=request.fps,
    #     frames_s=request.frames_s,
    #     data_index=request.data_index,
    #     multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
    #     upper_limit=request.upper_limit,
    #     lower_limit=request.lower_limit,
    #     auto_contrast = request.auto_contrast,
    #     auto_contrast_percentiles = request.auto_contrast_percentiles
    # )

    recipe = VideoRecipe.get_recipe_by_request(request)

    return orchestrator.create_video(recipe)



def get_dark_files_logic(request: GetDarkFilesRequest) -> str:
    if request.files_list is None or len(request.files_list) == 0:
        request.files_list = file.get_name_files(request.data_path)

    request.fit_format = class_registry[request.fit_format]

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
    # plt.show()
    plt.close()

    return result




def create_image_logic(request: CreateImageRequest):
    # logics.create_image(
    #     names_files=request.files_list,
    #     root_path=request.data_path,
    #     number=request.frame_number,
    #     flag_info=request.flag_info,
    #     name=request.general_title,
    #     cut=request.cut,
    #     percent_to_trim=request.percent_to_trim,
    #     save_folder=request.save_folder,
    #     figsize=request.figsize,
    #     fit_format=class_registry[request.fit_format],
    #     dark=request.dark,
    #     dark_name=request.dark_file_name,
    #     _zip=request.zipped_file,
    #     remove_single_pixels=request.remove_single_pixels,
    #     correct_matrix=request.correct_matrix_path,
    #     Rayleigh=request.rayleigh,
    #     result_matrix_safe_folder=request.result_matrix_save_folder,
    #     logfun=None,
    #     data_index=request.data_index,
    #     file_name=request.file_name,
    #     multiplication_on_correct_matrix=request.multiplication_on_correct_matrix,
    #     auto_contrast = request.auto_contrast,
    #     auto_contrast_percentiles = request.auto_contrast_percentiles
    # )
    recipe = ImageRecipe.get_recipe_by_request(request)

    orchestrator.create_image(recipe)

    return  os.path.join(request.save_folder, f'{request.file_name}.png')



def create_heatmap_logic(request: CreateHeatmapRequest):
    old_logicks.create_heatmap(
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
    # recipe = HeatmapRecipe.get_recipe_by_request(request)
    # for k, v in vars(recipe).items():
    #     print(f"{k} = {v}")
    # orchestrator.create_heatmap(recipe)

    return os.path.join(request.save_folder, f'{request.file_name}.png')



