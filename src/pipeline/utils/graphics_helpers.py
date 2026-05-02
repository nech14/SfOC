import cv2
import numpy as np
from pathlib import Path
from skimage.exposure import exposure
from skimage.measure import label, regionprops

def auto_contrast_skimage(data, p2=None, p98=None, auto_contrast_percentiles=[2, 98]):
    image = data.copy()
    non_zero_values = image[image > 0]
    if p2 is None or p98 is None:
        p2, p98 = np.percentile(non_zero_values, (auto_contrast_percentiles[0], auto_contrast_percentiles[1]))
    result = exposure.rescale_intensity(image, in_range=(p2, p98))
    return result, p2, p98


def cut_img(image, percent_to_trim=0.1, nan=True):
    height, width = image.shape
    radius = min(height, width) // 2

    center = (width // 2, height // 2)
    trim_radius = int(radius * percent_to_trim)

    mask = np.zeros((height, width), dtype=np.uint8)  # Используем тип uint8 для маски

    cv2.circle(mask, center, radius - trim_radius, 255, thickness=cv2.FILLED)  # Заполняем круг значением 255

    if nan:
        result_image = np.where(mask == 255, image, np.nan)  # Используем np.where для создания нового изображения с np.nan вместо 0
    else:
        result_image = np.where(mask == 255, image, 0)
    return result_image


def remove_single_pixels(data, log=False, label_diff_region=False, data_copy_del=False):

    blurred_image = cv2.GaussianBlur(data, (21, 21), 0)  # (5, 5) - размер ядра фильтра, 0 - стандартное отклонение

    diff = data - blurred_image
    cut_diff = cut_img(diff)

    cut1_diff = cut_diff.copy()
    cut1_diff[cut1_diff>60000] = np.nan
    cut1_diff[cut1_diff == np.nan] = False
    #cut1_diff[cut1_diff > 0] = True

    binary_diff = (cut1_diff > 0).astype(bool)

    label_diff = label(binary_diff)

    if log:
        print(f"Count labels on diff: {label_diff.max()}")

    regions = regionprops(label_diff)

    if label_diff_region:
        label_diff_region = label_diff.copy()

    data_copy = np.array(data.copy())

    if data_copy_del:
        data_copy_del = np.array(data.copy())

        for region in regions:
            if region.area < 2.:
                #label_diff_region[label_diff_region == region.label] = 0
                region_coords = region.coords
                for coord in region_coords:
                    data_copy_del[coord[0], coord[1]] = 0.

    for region in regions:
        if region.area < 2.:
            region_coords = region.coords
            #print(region_coords)
            #data_copy[int(region_coords[0]), int(region_coords[1])] = 0.
            for coord in region_coords:
                data_copy[coord[0], coord[1]] = 0.

            def interpolate_neighbours(image, coord):
                interpolated_values = []
                x, y = coord
                neighbours = []
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < image.shape[0] and 0 <= ny < image.shape[1] and (nx, ny) != (x, y):
                            neighbours.append(image[nx, ny])
                if neighbours:
                    interpolated_values.append(np.mean(neighbours))
                else:
                    interpolated_values.append(0)  # Если нет соседей, ставим 0
                return interpolated_values


            # Интерполируем значения для удаленных точек
            interpolated_values = interpolate_neighbours(data_copy, region_coords[0])

            # Запишем интерполированные значения обратно в копию изображения
            data_copy[region_coords[:, 0], region_coords[:, 1]] = interpolated_values

        elif label_diff_region is not False:
            label_diff_region[label_diff_region == region.label] = 0
            #del regions[region.label-1]
    if label_diff_region is not False and data_copy_del is not False:
        return data_copy, label_diff_region, data_copy_del
    if label_diff_region is not False:
        return data_copy, label_diff_region
    if data_copy_del is not False:
        return data_copy, data_copy_del
    return data_copy



def compress_by_2(img: np.ndarray) -> np.ndarray:
    # Убеждаемся, что форма делится на 2
    h, w = img.shape
    assert h % 2 == 0 and w % 2 == 0, "Размеры должны быть кратны 2"

    # 1. Ресайпим в 4D: (h//2, 2, w//2, 2)
    # 2. Считаем среднее по осям 1 и 3
    return img.reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))

def create_correct_matrix_new(  #need test
    count_compression: int =2,
    base_shape: int = 2048,
    path_file: Path = Path(
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