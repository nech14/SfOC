from pathlib import Path

import numpy as np


def compress_by_2(img: np.ndarray) -> np.ndarray:
    # Убеждаемся, что форма делится на 2
    h, w = img.shape
    assert h % 2 == 0 and w % 2 == 0, "Размеры должны быть кратны 2"

    # 1. Ресайпим в 4D: (h//2, 2, w//2, 2)
    # 2. Считаем среднее по осям 1 и 3
    return img.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))

def create_correct_matrix(  #need test
    path_file: Path,
    count_compression: int = 2,
    base_shape: int = 2048
):
    # Загружаем и преобразуем данные
    matrix = np.fromfile(path_file, dtype='float32')
    matrix2048 = matrix.reshape((base_shape, base_shape), order='F')

    # Применяем сжатие count_compression раз
    new_matrix = matrix2048
    for _ in range(count_compression):
        new_matrix = compress_by_2(new_matrix)

    return new_matrix


def create_correct_matrix_old(
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