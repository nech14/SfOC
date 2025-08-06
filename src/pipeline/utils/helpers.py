import datetime
import os
from typing import Any

import numpy as np

from src.file import file
from src.models.dark_data_model import DarkData
from src.pipeline.utils import graphics_helpers


def get_dark(names, new_path, check_name="DARK", _zip=True, fit_format=file.FitsInfo) -> (
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
        if not check_name in name:
            break

        name_path = os.path.join(new_path, name)
        info, data = file.open_gz(name_path, _zip=_zip)

        buf = np.vstack((buf, [data]))
        buf_time = np.append(buf_time, fit_format(info).get_datetime())

    return buf, buf_time


def get_dark_avg(names, root_path, dark_name="DARK", _zip=True, fit_format=file.FitsInfo) -> DarkData:
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
    path_file="C:/work/search_for_oxide_cloud/ALL SKY IMAGERS/Calibration SN10210/UNIFORMITY COEFFICIENT FILES/20190718_Russia-LZOS_KEO10210_5577L14002-02_0001000ms_G3_FOV180_uniformity_map_2048x2048.dat"
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

