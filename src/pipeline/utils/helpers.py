import datetime
import os
from typing import Tuple, Union, List

import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

from src.models.common_models.dark_data_model import DarkData
from src.models.fits_models.fits import FitsInfo
from src.models.images_models.abstract_img import AbstractImg
from src.utils.file import file


def get_dark(names, new_path, check_name="DARK", _zip=True, fit_format=FitsInfo) -> (
        None|tuple[np.ndarray, np.ndarray]
):
    if check_name in names[0]:
        name_path = os.path.join(new_path, names[0])
        info, data = file.open_gz(name_path, _zip=_zip)
        buf = np.array([data])
        buf_time = np.array([fit_format(info).get_datetime()])
    else:
        return None

    for name in names[1:]:
        # print(name)
        if not check_name in name:
            break

        name_path = os.path.join(new_path, name)
        info, data = file.open_gz(name_path, _zip=_zip)

        buf = np.vstack((buf, [data]))
        buf_time = np.append(buf_time, fit_format(info).get_datetime())

    return buf, buf_time


def get_dark_avg(names, root_path, dark_name="DARK", _zip=True, fit_format=FitsInfo) -> DarkData:
    dark_data, times = get_dark(names, root_path, dark_name, _zip=_zip, fit_format=fit_format)
    data_avg = (np.mean(dark_data, axis=0))

    # Получаем среднее время в секундах
    average_time_seconds = sum(dt.timestamp() for dt in times) / len(times)

    # Преобразовываем среднее значение времени обратно в формат datetime.datetime
    time_avg = datetime.datetime.fromtimestamp(average_time_seconds)

    return DarkData(data_avg, time_avg)


def subtract_noise_frame(dark_start: DarkData, dark_end: DarkData, data, date_time: datetime):
    k1 = (date_time - dark_start.time) / (dark_end.time-dark_start.time)
    k2 = (dark_end.time - date_time) / (dark_end.time-dark_start.time)

    fix_data = data.copy()
    fix_data = fix_data - (dark_start.frame*k2 + dark_end.frame*k1)/2
    return fix_data


def get_equal_intervals_integers(a, b, n):
    if n < 2:
        return [a] if n == 1 else []

    step = (b - a) // (n - 1)
    return [a + step * i for i in range(n)]



def calculate_frame_Rayleigh(data, info):
    A = np.float64(file.get_A(info.CCDGAIN, info.ROSPEED, info.DEVICEID))
    B = np.float64(info.BINNING*info.BINNING)
    t_exp = np.float64(info.EXPOSURE[:-2])/1000
    G = 1.

    data = data.copy()
    data = A * data / B * t_exp * G

    return data

def compress_by_2(img: np.ndarray) -> np.ndarray:
    # Убеждаемся, что форма делится на 2
    h, w = img.shape
    assert h % 2 == 0 and w % 2 == 0, "Размеры должны быть кратны 2"

    # 1. Ресайпим в 4D: (h//2, 2, w//2, 2)
    # 2. Считаем среднее по осям 1 и 3
    return img.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))

def create_correct_matrix_new(  #need test
    count_compression=2,
    base_shape=2048,
    path_file= Path(
        "C:/work/search_for_oxide_cloud/ALL SKY IMAGERS/Calibration SN10210/UNIFORMITY COEFFICIENT FILES/20190718_Russia-LZOS_KEO10210_5577L14002-02_0001000ms_G3_FOV180_uniformity_map_2048x2048.dat"
    )
):
    # Загружаем и преобразуем данные
    matrix = np.fromfile(path_file, dtype='float32')
    matrix2048 = matrix.reshape((base_shape, base_shape), order='F')

    # Применяем сжатие count_compression раз
    new_matrix = matrix2048
    for _ in range(count_compression):
        new_matrix = compress_by_2(new_matrix)

    return new_matrix

def create_correct_matrix(
        count_compression=2,
        base_shape=2048,
        path_file="C:/work/search_for_oxide_cloud/ALL SKY IMAGERS/Calibration SN10210/UNIFORMITY COEFFICIENT FILES/20190718_Russia-LZOS_KEO10210_5577L14002-02_0001000ms_G3_FOV180_uniformity_map_2048x2048.dat"
):
    matrix = np.fromfile(path_file, dtype='float32')

    matrix2048 = np.reshape(matrix, (base_shape, base_shape), order='F')

    new_matrix = matrix2048
    new_shape = base_shape
    for i in range(count_compression):
        new_shape //= 2
        old_matrix = new_matrix
        new_matrix = np.zeros((new_shape, new_shape))

        for i in range(new_shape):  # range(1,uc.shape[0],2):
            for j in range(new_shape):  # range(1,uc.shape[1],2):
                new_matrix[i, j] = np.mean(old_matrix[i*2:i*2+2, j*2:j*2+2])



    return new_matrix


def create_hists(image_first, image_second, diff, diff1=None, bins=2000,
                 xmin_data=0, xmax_data=6000, xmin_diff=-1000, xmax_diff=1000, alpha=0.5,
                 ymin_data=0, ymax_data=20000, ymin_diff=0, ymax_diff=30000, show=False,
                 figsize_x=16.54, figsize_y=5.12, return_data=False) -> Union[
    Tuple[np.ndarray, np.ndarray, List[mpatches.Patch]],
    np.ndarray
]:
    #15.36
    fig = plt.figure(figsize=(figsize_x, figsize_y))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.65, 1])

    ax1 = fig.add_subplot(gs[0, 0])
    result_hist = ax1.hist(image_first.flatten(), bins=bins)

    if return_data:
        if show:
            plt.show()
        plt.close()
        return result_hist

    if xmin_data is not None and xmax_data is not None:
        ax1.set_xlim(xmin=xmin_data, xmax=xmax_data)
    if ymin_data is not None and ymax_data is not None:
        ax1.set_ylim(ymin=ymin_data, ymax=ymax_data)

    result_hist1 = ax1.hist(image_second.flatten(), bins=bins, alpha=0.5)

    ax2 = fig.add_subplot(gs[0, 1])
    if diff1 is not None:
        result_hist_diff = ax2.hist(diff1.flatten(), bins=bins)
    else:
        alpha = 1
        result_hist_diff = None
    result_hist_diff1 = ax2.hist(diff.flatten(), bins=bins, alpha=alpha, color="orange")


    if xmin_diff is not None and xmax_diff is not None:
        ax2.set_xlim(xmin=xmin_diff, xmax=xmax_diff)
    if ymin_diff is not None and ymax_diff is not None:
        ax2.set_ylim(ymin=ymin_diff, ymax=ymax_diff)

    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.97, top=0.99, wspace=0.13, hspace=0)

    canvas = plt.gcf().canvas
    canvas.draw()
    rgb_string = canvas.buffer_rgba()

    image_array = np.frombuffer(rgb_string, dtype=np.uint8)
    image_array = image_array.reshape(canvas.get_width_height()[::-1] + (4,))

    if show:
        plt.show()
    else:
        plt.close()

    return image_array[:, :, :3]


def get_hist_parameters(img_first: AbstractImg, img_second: AbstractImg, bins=2000) \
        -> Tuple[float, float, float, float, float, float, float]:
    diff = img_first.data - img_second.data
    plt.figure(figsize=(10, 10))
    f_data = img_first.data.flatten()
    f_data1 = img_second.data.flatten()
    f_diff = diff.flatten()

    clean_data = img_first.data.flatten()
    clean_data = clean_data[np.isfinite(clean_data)]
    min_x = np.percentile(clean_data, 1) * 2
    max_x = np.percentile(clean_data, 99) * 2

    clean_data1 = img_second.data.flatten()
    clean_data1 = clean_data1[np.isfinite(clean_data1)]
    min_x1 = np.percentile(clean_data1, 1) * 2
    max_x1 = np.percentile(clean_data1, 99) * 2

    clean_diff = diff.flatten()
    clean_diff = clean_diff[np.isfinite(clean_diff)]
    min_d = np.percentile(clean_diff, 1) * 2
    max_d = np.percentile(clean_diff, 99) * 2

    counts, bin_edges, patches = plt.hist(f_data, bins=bins)
    counts1, bin_edges1, patches1 = plt.hist(f_data1, bins=bins)
    counts_d, bin_edges_d, patches_d = plt.hist(f_diff, bins=bins)

    plt.close()

    return min(min_x, min_x1, 0), max(max_x, max_x1), 0, max(max(counts*1.5), max(counts1*1.5)), min(0, min_d), max_d, max(counts_d*1.5)


def drive_to_color_palette(combined_image, dlimit, ulimit, cmap):

    buf_combined_image = np.nan_to_num(combined_image, nan=0)

    cmap_image = np.clip(buf_combined_image, dlimit, ulimit)
    cmap_image = (cmap_image - dlimit) / (ulimit - dlimit)  # Нормализация значений
    cmap_image = (cmap_image * 255).astype(np.uint8)  # Конвертация в формат uint8

    # Применение цветовой карты
    cmap_image = cmap(cmap_image)

    # Преобразование в BGR (OpenCV использует формат BGR)
    cmap_image = (cmap_image[:, :, 0] * 255).astype(np.uint8)
    return cmap_image[:, :]
