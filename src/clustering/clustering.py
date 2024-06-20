import os
from enum import Enum

import cv2
import hdbscan
import numpy as np

from SfOC.src import graphics, file
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, OPTICS, AgglomerativeClustering
from sklearn.neighbors import NearestNeighbors
from skimage.transform import resize
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.patches as patches
from scipy.signal import argrelextrema
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.metrics import silhouette_samples, silhouette_score
from scipy.spatial.distance import cdist
from sklearn.mixture import GaussianMixture


class BinShow(Enum):
    NONE = 0
    ALL = 3


def canny_frame_best(names_files, new_path, i, percent_to_trim=0.1, _zip=False, type_fits=file.FitsInfo2014, save_folder=None,
                     file_name=None, rows=5, cols=5, suptitle=None, nameFile="image", show=False, log=False, _resize=False,
                     eps_steep=0.5, min_samples_steep=10, eps_steep_start=0., min_samples_start_steep=0, cmap=None):

    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=False, type_fits=type_fits)

    if _resize:
        diff = resize(diff, (256, 256), anti_aliasing=True)

    plt.figure(figsize=(12, 12))

    if suptitle is None:
        suptitle = f"{info.get_datetime()}-{info1.get_datetime()} finding the best value for DBSCAN"
    plt.suptitle(suptitle)

    plt.subplot(rows, cols, 1)
    pp = 500
    plt.imshow(diff, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.title(f'Original')
    plt.axis('off')

    eps = eps_steep_start + eps_steep
    min_samples = min_samples_start_steep + min_samples_steep
    for i in range(1, rows * cols):
        plt.subplot(rows, cols, i + 1)

        if i%cols == 0:
            eps = eps_steep_start
            min_samples += min_samples_steep

        eps += eps_steep

        eps = round(eps, 1)

        # Получение координат и значений серого цвета
        x_coords, y_coords = np.meshgrid(np.arange(diff.shape[1]), np.arange(diff.shape[0]))
        features = np.column_stack((diff.ravel(), x_coords.ravel(), y_coords.ravel()))

        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean').fit(features)
        labels = dbscan.labels_

        # Преобразование результата кластеризации в изображение
        clustered_image = np.zeros_like(diff)
        unique_labels = set(labels)
        for label in unique_labels:
            if label == -1:
                # Обработка шума (контуры)
                clustered_image[labels.reshape(diff.shape) == label] = 0
            else:
                # Обработка кластеров (не-контуры)
                clustered_image[labels.reshape(diff.shape) == label] = 255

        plt.imshow(clustered_image, cmap=cmap)

        # Добавление заголовка с параметрами eps и min_samples
        plt.title(f'e={eps}, m={min_samples}')

        # Удаление осей для улучшения читаемости
        plt.axis('off')

        if log:
            print(f"create {i + 1}/{rows*cols}")


    if not save_folder is None:
        os.makedirs(save_folder, exist_ok=True)
        if file_name is None:
            file_name = f"{nameFile}.png"
        output_path = os.path.join(save_folder, file_name)
        plt.savefig(output_path)

    if show:
        plt.show()
    plt.close()



def canny_frame(names_files, new_path, i, percent_to_trim=0.1, _zip=False, type_fits=file.FitsInfo2014,
              eps=6, min_samples=10, return_diff=False, _resize=False, origin_diff=False):
    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=False, type_fits=type_fits)
    if origin_diff:
        origin_diff_return = diff
    if _resize:
        diff_resized = resize(diff, (256, 256), anti_aliasing=True)
        mask = np.ma.masked_equal(diff_resized, 0)
        diff = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))

    # Получение координат и значений серого цвета
    x_coords, y_coords = np.meshgrid(np.arange(diff.shape[1]), np.arange(diff.shape[0]))
    features = np.column_stack((diff.ravel(), x_coords.ravel(), y_coords.ravel()))

    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean').fit(features)
    labels = dbscan.labels_

    # Преобразование результата кластеризации в изображение
    clustered_image = np.zeros_like(diff)
    unique_labels = set(labels)
    for label in unique_labels:
        if label == -1:
            # Обработка шума (контуры)
            clustered_image[labels.reshape(diff.shape) == label] = 0
        else:
            # Обработка кластеров (не-контуры)
            clustered_image[labels.reshape(diff.shape) == label] = 255

    if return_diff and origin_diff:
        return clustered_image, diff, origin_diff_return
    elif origin_diff:
        return clustered_image, origin_diff_return
    elif return_diff:
        return clustered_image, diff
    return clustered_image


def bin_frame_best(names_files, new_path, i, percent_to_trim=0.1, _zip=False, type_fits=file.FitsInfo2014, save_folder=None,
              file_name=None, rows=5, cols=5, suptitle=None, nameFile="image", show=False,
              eps_steep=0.5, min_samples_steep=10, eps_steep_start=0., min_samples_start_steep=0):
    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=_zip, type_fits=type_fits)

    diff_resized = resize(diff, (256, 256), anti_aliasing=True)
    mask = np.ma.masked_equal(diff_resized, 0)
    small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
    w, h = small_image.shape
    image_array = small_image.reshape(-1, 1)


    plt.figure(figsize=(12, 12))

    if suptitle is None:
        suptitle = f"{info.get_datetime()}-{info1.get_datetime()} finding the best value for DBSCAN"
    plt.suptitle(suptitle)


    plt.subplot(rows, cols, 1)
    pp = 500
    plt.imshow(diff, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.title(f'Original')
    plt.axis('off')

    eps = eps_steep_start + eps_steep
    min_samples = min_samples_start_steep + min_samples_steep
    for i in range(1, rows*cols):
        plt.subplot(rows, cols, i+1)

        if i%cols == 0:
            eps = eps_steep_start
            min_samples += min_samples_steep

        eps += eps_steep

        eps = round(eps, 1)

        dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(image_array)
        labels = dbscan.labels_
        segmented_image = labels.reshape(w, h)
        d_segmented_image = segmented_image.copy()
        d_segmented_image[d_segmented_image != -1] = 0
        d_segmented_image[d_segmented_image == -1] = 1

        plt.imshow(d_segmented_image)

        # Добавление заголовка с параметрами eps и min_samples
        plt.title(f'e={eps}, m={min_samples}')

        # Удаление осей для улучшения читаемости
        plt.axis('off')




    if not save_folder is None:
        os.makedirs(save_folder, exist_ok=True)
        if file_name is None:
            file_name = f"{nameFile}.png"
        output_path = os.path.join(save_folder, file_name)
        plt.savefig(output_path)

    if show:
        plt.show()
    plt.close()

def bin_frame(names_files, new_path, i, percent_to_trim=0.1, _zip=False, type_fits=file.FitsInfo2014, save_folder=None,
              file_name=None, name_bin="bin", bin_time_frame=None, type_print=BinShow.NONE,
              eps=1.2, min_samples=50):
    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=_zip, type_fits=type_fits)

    diff_resized = resize(diff, (256, 256), anti_aliasing=True)
    mask = np.ma.masked_equal(diff_resized, 0)
    small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
    w, h = small_image.shape
    image_array = small_image.reshape(-1, 1)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(image_array)
    labels = dbscan.labels_
    segmented_image = labels.reshape(w, h)
    d_segmented_image = segmented_image.copy()
    d_segmented_image[d_segmented_image != -1] = 0
    d_segmented_image[d_segmented_image == -1] = 1


    coords = np.column_stack(np.where(d_segmented_image == 1))
    if not bin_time_frame is None:
        bin_time_frame.append(f'{info.get_norm_time()}')
        bin_time_frame.append(f'{info1.get_norm_time()}')


    if type_print != BinShow.NONE:
        plt.subplot(131)
        pp= 500
        plt.imshow(diff, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)

        plt.subplot(132)
        plt.imshow(segmented_image)

        plt.subplot(133)
        plt.imshow(d_segmented_image)
        plt.show()


    if not save_folder is None:
        os.makedirs(save_folder, exist_ok=True)
        if file_name is None:
            file_name = f"{i}.png"
        output_path = os.path.join(save_folder, name_bin, file_name)
        plt.savefig(output_path)

    return coords, f'{info.get_datetime()} \n {info1.get_datetime()}', mask, diff_resized


def model_method_frame_GaussianMixture(names_files, new_path):
    _zip = False
    i = 123
    # i = 358
    # i = 21
    start = 121
    end = 126
    # start = 20
    # end = 25
    # i=359

    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=_zip, type_fits=file.FitsInfo2014)

    diff_resized = resize(diff, (256, 256), anti_aliasing=True)
    mask = np.ma.masked_equal(diff_resized, 0)
    small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
    w, h = small_image.shape
    image_array = small_image.reshape(-1, 1)
    dbscan = DBSCAN(eps=1.2, min_samples=50).fit(image_array)
    labels = dbscan.labels_
    segmented_image = labels.reshape(w, h)
    segmented_image[segmented_image != -1] = 0
    segmented_image[segmented_image == -1] = 1
    d_segmented_image = segmented_image.copy()

    # Извлечение координат пикселей, имеющих значение 1
    coords = np.column_stack(np.where(d_segmented_image == 1))
    plt.imshow(d_segmented_image)
    plt.show()

    X = d_segmented_image.copy()

    # Диапазон возможных значений количества кластеров
    n_components_range = range(2, 20)
    silhouette_scores = []

    for n_components in n_components_range:
        gmm = GaussianMixture(n_components=n_components, random_state=0, covariance_type="spherical")
        labels = gmm.fit_predict(coords)
        silhouette_avg = silhouette_score(coords, labels)
        silhouette_scores.append(silhouette_avg)

    # Визуализация силуэтных коэффициентов
    plt.plot(n_components_range, silhouette_scores, marker='o')
    plt.xlabel('Количество кластеров')
    plt.ylabel('Силуэтный коэффициент')
    plt.title('Силуэтный коэффициент при разных количествах кластеров')
    plt.show()

    # Определение оптимального количества кластеров
    optimal_n_components = n_components_range[np.argmax(silhouette_scores)]
    print(f'Оптимальное количество кластеров: {optimal_n_components}')

    # Создание и обучение модели Gaussian Mixture
    gmm = GaussianMixture(n_components=optimal_n_components, random_state=0, covariance_type="spherical")
    gmm.fit(coords)

    # Предсказание кластеров
    labels = gmm.predict(coords)

    for (x, y), color in zip(coords, labels):
        X[x][y] = color+1

    plt.subplot(121)
    plt.imshow(d_segmented_image)
    # Визуализация результатов
    plt.subplot(122)
    plt.imshow(X)
    # plt.scatter(coords[:, 0], coords[:, 1], c=labels, s=40)
    plt.show()



def model_method_frames_GaussianMixture(names_files, new_path, save_folder=None, start=18, end=25, log=False):
    _zip = False
    # i = 22
    # start = 120
    # end = 127
    # start = 20
    # end = 25
    # start = 354
    # end = 361
    # i=359

    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    diffs_base = []
    base = [0, 0, 0]
    n = 0
    steep = 2.5

    name_info = []
    name_info2 = []

    for i in range(start, end):
        data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                        _zip=_zip, type_fits=file.FitsInfo2014)

        diff_resized = resize(diff, (256, 256), anti_aliasing=True)
        mask = np.ma.masked_equal(diff_resized, 0)
        small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
        w, h = small_image.shape
        image_array = small_image.reshape(-1, 1)
        dbscan = DBSCAN(eps=1.2, min_samples=50).fit(image_array)
        labels = dbscan.labels_
        segmented_image = labels.reshape(w, h)
        segmented_image[segmented_image != -1] = 0
        segmented_image[segmented_image == -1] = 1
        d_segmented_image = segmented_image.copy()

        # Извлечение координат пикселей, имеющих значение 1
        diffs_base.append(mask)
        coords = np.column_stack(np.where(d_segmented_image == 1))
        base = np.vstack((base, np.column_stack((np.full(coords.shape[0], n), coords))))
        name_info.append(f'{info.get_datetime()} \n {info1.get_datetime()}')
        name_info2.append(f'{info.get_norm_time()}')
        name_info2.append(f'{info1.get_norm_time()}')
        # plt.imshow(d_segmented_image)
        # plt.show()
        diffs_base.append(diff_resized)
        n += steep

        if not save_folder is None:
            os.makedirs(save_folder + '\\bin_GM', exist_ok=True)
            file_name = f"{start}-{end}.png"
            output_path = os.path.join(save_folder, 'bin_GM', file_name)
            plt.savefig(output_path)
    diffs_base = np.array(diffs_base)
    data = base

    # Найдем оптимальное количество кластеров с использованием коэффициента силуэта
    # Диапазон возможных значений количества кластеров
    n_components_range = range(2, 10)
    silhouette_scores = []
    for n_components in n_components_range:
        gmm = GaussianMixture(n_components=n_components, random_state=0, covariance_type="spherical")
        labels = gmm.fit_predict(data)
        silhouette_avg = silhouette_score(data, labels)
        silhouette_scores.append(silhouette_avg)

    # Определение оптимального количества кластеров
    optimal_n_components = n_components_range[np.argmax(silhouette_scores)]
    # print(f'Оптимальное количество кластеров: {optimal_n_components}')

    # Создание и обучение модели Gaussian Mixture
    gmm = GaussianMixture(n_components=optimal_n_components, random_state=0, covariance_type="spherical")
    gmm.fit(data)

    # Предсказание кластеров
    labels = gmm.predict(data)
    unique_labels = set(labels)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for label in unique_labels:
        cluster_data = data[labels == label]
        ax.scatter(cluster_data[:, 0], cluster_data[:, 1], cluster_data[:, 2], label=f'Cluster {label}')

    ax.set_title(f"best {optimal_n_components}")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('T')
    plt.legend()

    if not save_folder is None:
        os.makedirs(save_folder + '\\cut3D_GM', exist_ok=True)
        file_name = f"{start}-{end}.png"
        output_path = os.path.join(save_folder, 'cut3D_GM', file_name)
        plt.savefig(output_path)

    # Создание подграфиков
    fig, axes = plt.subplots(1, 7, figsize=(20, 3))
    n = -0.5
    for frame, ax in enumerate(axes, start=1):
        mask = np.ma.masked_equal(diffs_base[frame - 1], 0)
        ax.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
        ax.set_title(f'{name_info[frame-1]}')
        # ax.set_title(f'Frame {frame}')

        # Нанесение точек на изображения
        for label in unique_labels:
            cluster_data = data[labels == label]
            cluster_data_z = cluster_data[cluster_data[:, 0] == (frame - 1) * steep]
            ax.scatter(cluster_data_z[:, 2] * 2, cluster_data_z[:, 1] * 2, label=f'Cluster {label}')

        # Отображение легенды только на последнем подграфике
    plt.tight_layout()

    if not save_folder is None:
        os.makedirs(save_folder + '\\cut_GM', exist_ok=True)
        file_name = f"{start}-{end}.png"
        output_path = os.path.join(save_folder, 'cut_GM', file_name)
        plt.savefig(output_path)


    if log:
        print(f"create {start}-{end}")

    plt.close()
    # plt.show()
    return optimal_n_components, name_info2


def model_method_frame(names_files, new_path):
    _zip = False
    i = 123
    i = 358
    start = 121
    end = 126
    # start = 20
    # end = 25
    # i=359

    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=_zip, type_fits=file.FitsInfo2014)

    diff_resized = resize(diff, (256, 256), anti_aliasing=True)
    mask = np.ma.masked_equal(diff_resized, 0)
    small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
    w, h = small_image.shape
    image_array = small_image.reshape(-1, 1)
    dbscan = DBSCAN(eps=1.2, min_samples=50).fit(image_array)
    labels = dbscan.labels_
    segmented_image = labels.reshape(w, h)
    segmented_image[segmented_image != -1] = 0
    segmented_image[segmented_image == -1] = 1
    d_segmented_image = segmented_image.copy()


    # Извлечение координат пикселей, имеющих значение 1
    coords = np.column_stack(np.where(d_segmented_image == 1))
    plt.imshow(d_segmented_image)
    plt.show()

    # Найдем оптимальное количество кластеров с использованием коэффициента силуэта
    range_n_clusters = [i for i in range(2, 20)]
    best_n_clusters = 2
    best_silhouette_avg = -1

    for n_clusters in range_n_clusters:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(coords)

        # Вычисляем силуэт без учета выбросов
        silhouette_avg = silhouette_score(coords, cluster_labels)
        print(f"Для {n_clusters} кластеров средний коэффициент силуэта: {silhouette_avg}")

        if silhouette_avg > best_silhouette_avg:
            best_silhouette_avg = silhouette_avg
            best_n_clusters = n_clusters
    print(f"best {best_n_clusters}")
    # Проведем окончательную кластеризацию с лучшим количеством кластеров
    kmeans = KMeans(n_clusters=best_n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(coords)

    X = d_segmented_image.copy()
    for (x, y), color in zip(coords, cluster_labels):
        X[x][y] = color+1

    # Визуализируем исходное бинарное изображение и раскрашенное изображение кластеров
    fig, ax = plt.subplots(1, 2, figsize=(15, 7))

    ax[0].imshow(d_segmented_image, cmap='gray')
    ax[0].set_title("Исходное бинарное изображение")

    ax[1].imshow(X)
    ax[1].set_title(f"Изображение с {best_n_clusters} кластерами (по K-means)")

    plt.show()




def model_method_frames(names_files, new_path, save_folder=None, start=18, end=25, log=False):
    _zip = False
    # i = 22
    # start = 120
    # end = 127
    # start = 20
    # end = 25
    # start = 354
    # end = 361
    # i=359

    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    diffs_base = []
    base = [0, 0, 0]
    n = 0
    steep = 0.5

    name_info = []
    name_info2 = []

    for i in range(start, end):
        data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                        _zip=_zip, type_fits=file.FitsInfo2014)

        diff_resized = resize(diff, (256, 256), anti_aliasing=True)
        mask = np.ma.masked_equal(diff_resized, 0)
        small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
        w, h = small_image.shape
        image_array = small_image.reshape(-1, 1)
        dbscan = DBSCAN(eps=1.2, min_samples=50).fit(image_array)
        labels = dbscan.labels_
        segmented_image = labels.reshape(w, h)
        segmented_image[segmented_image != -1] = 0
        segmented_image[segmented_image == -1] = 1
        d_segmented_image = segmented_image.copy()

        # Извлечение координат пикселей, имеющих значение 1
        diffs_base.append(mask)
        coords = np.column_stack(np.where(d_segmented_image == 1))
        base = np.vstack((base, np.column_stack((np.full(coords.shape[0], n), coords))))
        name_info.append(f'{info.get_datetime()} \n {info1.get_datetime()}')
        name_info2.append(f'{info.get_norm_time()}')
        name_info2.append(f'{info1.get_norm_time()}')
        # plt.imshow(d_segmented_image)
        # plt.show()
        diffs_base.append(diff_resized)
        n += steep

        if not save_folder is None:
            os.makedirs(save_folder + '\\binMMF', exist_ok=True)
            file_name = f"{start}-{end}.png"
            output_path = os.path.join(save_folder, 'binMMF', file_name)
            plt.savefig(output_path)

    diffs_base = np.array(diffs_base)
    data = base

    # Найдем оптимальное количество кластеров с использованием коэффициента силуэта
    range_n_clusters = [i for i in range(3, 20)]
    best_n_clusters = 2
    best_silhouette_avg = -1

    for n_clusters in range_n_clusters:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(coords)

        # Вычисляем силуэт без учета выбросов
        silhouette_avg = silhouette_score(coords, cluster_labels)
        #print(f"Для {n_clusters} кластеров средний коэффициент силуэта: {silhouette_avg}")

        if silhouette_avg > best_silhouette_avg:
            best_silhouette_avg = silhouette_avg
            best_n_clusters = n_clusters
    # Проведем окончательную кластеризацию с лучшим количеством кластеров
    kmeans = KMeans(n_clusters=best_n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(data)
    unique_labels = set(cluster_labels)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for label in unique_labels:
        cluster_data = data[cluster_labels == label]
        ax.scatter(cluster_data[:, 0], cluster_data[:, 1], cluster_data[:, 2], label=f'Cluster {label}')

    ax.set_title(f"best {best_n_clusters}")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('T')
    plt.legend()

    if not save_folder is None:
        os.makedirs(save_folder + '\\cut3DMMF', exist_ok=True)
        file_name = f"{start}-{end}.png"
        output_path = os.path.join(save_folder, 'cut3DMMF', file_name)
        plt.savefig(output_path)

    # Создание подграфиков
    fig, axes = plt.subplots(1, 7, figsize=(20, 3))
    n = -0.5
    for frame, ax in enumerate(axes, start=1):
        mask = np.ma.masked_equal(diffs_base[frame - 1], 0)
        ax.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
        ax.set_title(f'{name_info[frame-1]}')
        # ax.set_title(f'Frame {frame}')

        # Нанесение точек на изображения
        for label in unique_labels:
            cluster_data = data[cluster_labels == label]
            cluster_data_z = cluster_data[cluster_data[:, 0] == (frame - 1) * steep]
            ax.scatter(cluster_data_z[:, 2] * 2, cluster_data_z[:, 1] * 2, label=f'Cluster {label}')

        # Отображение легенды только на последнем подграфике
    plt.tight_layout()

    if not save_folder is None:
        os.makedirs(save_folder + '\\cutMMF', exist_ok=True)
        file_name = f"{start}-{end}.png"
        output_path = os.path.join(save_folder, 'cutMMF', file_name)
        plt.savefig(output_path)

    #
    # for frame in range(1, 6):
    #     plt.subplot(1, 5, frame)
    #     mask = np.ma.masked_equal(diffs_base[frame - 1], 0)
    #     plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    #     plt.colorbar(shrink=0.8, fraction=0.1)

    if log:
        print(f"create {start}-{end}")

    plt.close()
    # plt.show(
    return best_n_clusters, name_info2

def find_optimal_dbscan_params(data, eps_range, min_samples_range):
    best_eps = None
    best_min_samples = None
    best_silhouette_score = -1

    for eps in eps_range:
        for min_samples in min_samples_range:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = dbscan.fit_predict(data)

            # Оценка должна быть произведена только если более одного кластера
            if len(set(cluster_labels)) > 1 and -1 in cluster_labels:
                silhouette_avg = silhouette_score(data, cluster_labels)

                if silhouette_avg > best_silhouette_score:
                    best_silhouette_score = silhouette_avg
                    best_eps = eps
                    best_min_samples = min_samples

    return best_eps, best_min_samples, best_silhouette_score

def start(names_files, new_path, save_folder=None, start=18, end=25, log=False):
    _zip = False
    # i = 22
    # start = 120
    # end = 127
    # start = 18
    # end = 25
    # start = 356
    # end = 363
    # i=359
    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    diffs_base = []
    base = [0, 0, 0]
    n = 0
    steep = 5 #3.5

    # # Определите структурный элемент
    # kernel = np.ones((3, 3), np.uint8)

    name_info = []
    name_info2 = []

    fig, axes = plt.subplots(2, 7, figsize=(20, 6))
    for i in range(start, end):
        data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                        _zip=_zip, type_fits=file.FitsInfo2014)

        diff_resized = resize(diff, (256, 256), anti_aliasing=True)
        mask = np.ma.masked_equal(diff_resized, 0)
        small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
        w, h = small_image.shape
        image_array = small_image.reshape(-1, 1)
        dbscan = DBSCAN(eps=1.2, min_samples=50).fit(image_array)
        # dbscan = DBSCAN(eps=0.2, min_samples=10).fit(image_array)
        labels = dbscan.labels_
        segmented_image = labels.reshape(w, h)
        axes[1][i - start].imshow(segmented_image)
        segmented_image[segmented_image != -1] = 0
        segmented_image[segmented_image == -1] = 1
        d_segmented_image = segmented_image.copy()

        # d_segmented_image = d_segmented_image.astype(np.uint8)
        # d_segmented_image = cv2.morphologyEx(d_segmented_image, cv2.MORPH_OPEN, kernel)
        # d_segmented_image = cv2.morphologyEx(d_segmented_image, cv2.MORPH_CLOSE, kernel)



        # plt.imshow(d_segmented_image)
        # plt.show()

        coords = np.column_stack(np.where(d_segmented_image == 1))
        base = np.vstack((base, np.column_stack((np.full(coords.shape[0], n), coords))))

        name_info.append(f'{info.get_datetime()} \n {info1.get_datetime()}')
        name_info2.append(f'{info.get_norm_time()}')
        name_info2.append(f'{info1.get_norm_time()}')

        axes[0][i-start].set_title(name_info[-1])
        axes[0][i-start].imshow(d_segmented_image)

        diffs_base.append(diff_resized)
        n += steep

    if not save_folder is None:
        os.makedirs(save_folder + '\\bin', exist_ok=True)
        file_name = f"{start}-{end}.png"
        output_path = os.path.join(save_folder, 'bin', file_name)
        plt.savefig(output_path)

    # return
    diffs_base = np.array(diffs_base)
    data = base
    # print(data.shape)
    # print(data)

    # Диапазон значений для параметров eps и min_samples

    # Указание параметров для DBSCAN
    eps = 10.
    min_samples = 100

    # # Выполнение кластеризации
    # dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    # labels = dbscan.fit_predict(data)

    # clusterer = hdbscan.HDBSCAN(min_cluster_size=5,min_samples=80, max_cluster_size=1000)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=10)
    labels = clusterer.fit_predict(data)


    # clusterer = hdbscan.HDBSCAN(min_cluster_size=5,min_samples=80)
    # clusterer = hdbscan.HDBSCAN(min_cluster_size=30)
    # clusterer = hdbscan.HDBSCAN(min_cluster_size=75, max_cluster_size=2000)

    # Оценка ширины полосы (bandwidth) для Mean Shift
    # bandwidth = estimate_bandwidth(data, quantile=0.2, n_samples=100)
    # clusterer = MeanShift(bandwidth=bandwidth)
    # clusterer = OPTICS(min_samples=5)

    # min_samples = 100
    #
    # from kneed import KneeLocator
    #
    # # Построение графика расстояний до k-го ближайшего соседа
    # neighbors = NearestNeighbors(n_neighbors=min_samples)
    # neighbors_fit = neighbors.fit(data)
    # distances, indices = neighbors_fit.kneighbors(data)
    # distances = np.sort(distances[:, min_samples - 1])
    #
    # # Определение "колена" с использованием KneeLocator
    # kneedle = KneeLocator(range(1, len(distances) + 1), distances, S=1.0, curve="convex", direction="increasing")
    # eps = distances[kneedle.knee]
    # print(f"Оптимальное значение eps: {eps}")
    #
    #
    # clusterer = DBSCAN(eps=eps, min_samples=min_samples)

    # Печать результатов
    # print(f"Этикетки кластеров: {labels}")

    #Визуализация результатов (по желанию)

    unique_labels = set(labels)
    unique_labels.discard(-1)
    # unique_labels.discard(0)
    # unique_labels.discard(2)

    # print(unique_labels)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for label in unique_labels:
        cluster_data = data[labels == label]
        ax.scatter(cluster_data[:, 0], cluster_data[:, 1], cluster_data[:, 2], label=f'Cluster {label}')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('T')
    plt.legend()

    if not save_folder is None:
        os.makedirs(save_folder + '\\cut3D', exist_ok=True)
        file_name = f"{start}-{end}.png"
        output_path = os.path.join(save_folder, 'cut3D', file_name)
        plt.savefig(output_path)


    # Создание подграфиков
    fig, axes = plt.subplots(1, 7, figsize=(20, 3))
    n = -0.5
    for frame, ax in enumerate(axes, start=1):
        mask = np.ma.masked_equal(diffs_base[frame - 1], 0)
        ax.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
        ax.set_title(f'{name_info[frame-1]}')
        # ax.set_title(f'Frame {frame}')

        # Нанесение точек на изображения
        for label in unique_labels:
            cluster_data = data[labels == label]
            cluster_data_z = cluster_data[cluster_data[:, 0] == (frame-1)*steep]
            ax.scatter(cluster_data_z[:, 2]*2, cluster_data_z[:, 1]*2, label=f'Cluster {label}')



    # Отображение легенды только на последнем подграфике
    plt.tight_layout()

    if not save_folder is None:
        os.makedirs(save_folder + '\\cut', exist_ok=True)
        file_name = f"{start}-{end}.png"
        output_path = os.path.join(save_folder, 'cut', file_name)
        plt.savefig(output_path)

    #
    # for frame in range(1, 6):
    #     plt.subplot(1, 5, frame)
    #     mask = np.ma.masked_equal(diffs_base[frame - 1], 0)
    #     plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    #     plt.colorbar(shrink=0.8, fraction=0.1)

    if log:
        print(f"create {start}-{end}")

    plt.close()
    # plt.show()


    return max(set(labels)), name_info2

def start1(names_files, new_path):
    _zip = False
    # i = 22
    start = 120
    end = 127
    # start = 20
    # end = 25
    # i=359

    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    diffs_base = []
    base = [0, 0]
    for i in range(start, end):
        data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                        _zip=_zip, type_fits=file.FitsInfo2014)

        diff_resized = resize(diff, (256, 256), anti_aliasing=True)
        mask = np.ma.masked_equal(diff_resized, 0)
        small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
        w, h = small_image.shape
        image_array = small_image.reshape(-1, 1)
        dbscan = DBSCAN(eps=0.2, min_samples=100).fit(image_array)
        labels = dbscan.labels_
        segmented_image = labels.reshape(w, h)
        segmented_image[segmented_image != -1] = 0
        segmented_image[segmented_image == -1] = 1
        d_segmented_image = segmented_image.copy()

        # Извлечение координат пикселей, имеющих значение 1
        coords = np.column_stack(np.where(d_segmented_image == 1))
        base = np.vstack((base, coords))
        diffs_base.append(mask)

    diffs_base = np.array(diffs_base)
    # diffs = diffs_base.copy()
    # # Преобразование трехмерного массива в двумерный массив (подходит для DBSCAN)
    # n_samples = diffs.shape[0]
    # data_reshaped = diffs.reshape((n_samples, -1))

    # Применение алгоритма DBSCAN для кластеризации данных
    dbscan = DBSCAN(eps=2.0, min_samples=50)  # Настройте параметры eps и min_samples по вашему усмотрению
    labels = dbscan.fit_predict(base)


    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f'Количество кластеров: {n_clusters}')
    print(f'Количество шумовых точек: {n_noise}')

    mask = np.ma.masked_equal(diffs_base[0], 0)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)
    #

    unique_labels = set(labels)
    unique_labels.discard(-1)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    #
    for k, col in zip(unique_labels, colors):
        class_member_mask = (labels == k)

        xy = base[class_member_mask]
        plt.plot(xy[:, 1] * 2, xy[:, 0] * 2, 'o', markerfacecolor=tuple(col),
                 markeredgewidth=0, markersize=2)

    plt.show()

def start_2(names_files, new_path):
    _zip = False
    # i = 22
    start = 121
    end = 126
    start = 20
    end = 25
    # i=359

    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    diffs = []

    for i in range(start, end):
        data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                        _zip=_zip, type_fits=file.FitsInfo2014)

        mask = np.ma.masked_equal(diff, 0)
        diffs.append(mask)

    diffs = np.array(diffs)
    n_samples, height, width = diffs.shape

    # Преобразование кадров в одномерные массивы
    diffs_reshaped = diffs.reshape(n_samples, -1)
    image = diffs[0]

    # Уменьшение разрешения изображения
    image_resized = resize(image, (256, 256), anti_aliasing=True)

    # Создание координатной сетки и объединение с интенсивностью пикселей
    x, y = np.indices(image_resized.shape)
    image_reshape = np.c_[x.ravel(), y.ravel(), image_resized.ravel()]

    # Применение алгоритма HDBSCAN
    clusterer = hdbscan.HDBSCAN(min_cluster_size=500)
    cluster_labels = clusterer.fit_predict(image_reshape)
    labels = cluster_labels.reshape(image_resized.shape)

    # Подсчет количества уникальных кластеров, исключая шум (-1)
    unique_labels = set(cluster_labels)
    unique_labels.discard(-1)  # Удалить метку шума
    n_clusters = len(unique_labels)

    print(f"Количество кластеров: {n_clusters}")

    # Подготовка цветов для кластеров


    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels) + 1)]
    color_map = {label: col[:3] for label, col in zip(unique_labels, colors)}

    plt.figure(figsize=(10, 7))


    mask = np.ma.masked_equal(image_resized, 0)
    plt.subplot(121)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)

    plt.subplot(122)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)

    # Наложение точек кластеров поверх изображения
    for label in unique_labels:
        class_member_mask = (labels == label)
        xy = np.column_stack(np.where(class_member_mask))
        plt.scatter(xy[:, 1], xy[:, 0], s=10, c=[color_map[label]], label=f'Cluster {label}')

    plt.title('HDBSCAN Clustering on Image')
    plt.show()


def start_1(names_files, new_path):
    _zip = False
    # i = 22
    start = 121
    end = 126
    # i=359
    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    diffs = []

    for i in range(start, end):
        data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                        _zip=_zip, type_fits=file.FitsInfo2014)

        diffs.append(np.ma.masked_equal(diff, 0))

    diffs= np.array(diffs)

    # plt.imshow(diffs[3], cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    # plt.show()
    flattened_data = diffs.reshape(diffs.shape[0], -1)
    print(diffs.shape)
    print(flattened_data.shape)



    # Нормализация данных
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(flattened_data)

    # Применение DBSCAN для кластеризации
    dbscan = DBSCAN(eps=500., min_samples=50)
    clusters = dbscan.fit_predict(flattened_data)

    # Подсчет количества кластеров (исключая шумовые точки)
    n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
    print(f"Number of clusters: {n_clusters}")

    # Уменьшение размерности до 3D для визуализации с помощью PCA
    pca = PCA(n_components=3)
    reduced_data = pca.fit_transform(flattened_data)

    # Визуализация результатов в 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    unique_labels = set(clusters)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Черный цвет для шума
            col = [0, 0, 0, 1]

        class_member_mask = (clusters == k)
        xyz = reduced_data[class_member_mask]

        ax.scatter(xyz[:, 0], xyz[:, 1], xyz[:, 2], color=tuple(col), edgecolor='k', s=100)

    ax.set_title('DBSCAN clustering of frames in 3D')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.set_zlabel('Principal Component 3')
    plt.show()



def work_with_date(names_files, new_path, i, percent_to_trim=0.1, _zip=False, type_fits=file.FitsInfo):
    name_path = os.path.join(new_path, names_files[i])
    info, data = file.open_gz(name_path, _zip=_zip)
    # data = data[0]

    name_path1 = os.path.join(new_path, names_files[i + 1])
    info1, data1 = file.open_gz(name_path1, _zip=_zip)
    # data1 = data1[0]

    data = graphics.remove_single_pixels(data, False, False, False)
    data1 = graphics.remove_single_pixels(data1, False, False, False)

    data = graphics.cut_img(data, percent_to_trim, nan=False)
    data1 = graphics.cut_img(data1, percent_to_trim, nan=False)

    diff = data.astype(float) - data1.astype(float)
    return data, data1, diff, type_fits(info), type_fits(info1)


def get_clusters(names_files, new_path, i, _zip=False, percent_to_trim=0.1,  min_area_threshold=1950,
                 max_area_threshold=50000, eps_l=7.5, min_samples_l=100):

    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=_zip, type_fits=file.FitsInfo2014)

    mask = np.ma.masked_equal(diff, 0)
    small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
    w, h = small_image.shape
    image_array = small_image.reshape(-1, 1)
    dbscan = DBSCAN(eps=0.2, min_samples=100).fit(image_array)
    labels = dbscan.labels_
    segmented_image = labels.reshape(w, h)
    segmented_image[segmented_image != -1] = 0
    segmented_image[segmented_image == -1] = 1
    d_segmented_image = segmented_image.copy()


    # Извлечение координат пикселей, имеющих значение 1
    coords = np.column_stack(np.where(d_segmented_image == 1))

    dbscan = DBSCAN(eps=eps_l, min_samples=min_samples_l).fit(coords)
    labels = dbscan.labels_

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f'Количество кластеров: {n_clusters}')
    print(f'Количество шумовых точек: {n_noise}')

    unique_labels = set(labels)
    unique_labels.discard(-1)

    unique_labels = set(labels)
    unique_labels.discard(-1)  # Удаляем метку шума

    # Список для хранения центров кластеров и их прямоугольников
    cluster_centers = []
    rectangles = []

    for k in unique_labels:
        class_member_mask = (labels == k)
        xy = coords[class_member_mask]

        # Вычисляем центр кластера
        center = xy.mean(axis=0) * 2
        cluster_centers.append(center)

        # Вычисляем координаты прямоугольника
        min_coords = xy.min(axis=0) * 2
        max_coords = xy.max(axis=0) * 2

        # Вычисляем площадь прямоугольника
        area = (max_coords[0] - min_coords[0]) * (max_coords[1] - min_coords[1])
        if min_area_threshold <= area <= max_area_threshold:
            rectangles.append((min_coords, max_coords))

    return cluster_centers, rectangles


def base_lvl(names_files, new_path):
    _zip = False
    # i = 22
    i=125
    # i=359
    min_area_threshold = 1950
    max_area_threshold = 50000
    # eps_l = 6.5
    eps_l = 7.5
    # min_samples_l = 50
    min_samples_l = 100
    pp = 500
    percent_to_trim = 0.1

    data, data1, diff, info, info1 = work_with_date(names_files, new_path, i, percent_to_trim=percent_to_trim,
                                                    _zip=_zip, type_fits=file.FitsInfo2014)

    plt.subplot(431)
    plt.imshow(data, cmap="gray", vmax=pp*2)
    plt.colorbar(shrink=0.8, fraction=0.1)

    plt.subplot(432)
    plt.imshow(data1, cmap="gray", vmax=pp*2)
    plt.colorbar(shrink=0.8, fraction=0.1)

    plt.subplot(433)
    mask = np.ma.masked_equal(diff, 0)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)

    plt.subplot(434)
    mask = np.ma.masked_equal(diff, 0)
    mask[mask < 0] = 0
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)

    plt.subplot(435)
    mask = np.ma.masked_equal(diff, 0)
    mask[mask > 0] = 0
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)

    plt.subplot(436)
    mask = np.ma.masked_equal(diff, 0)
    mask = abs(mask)
    plt.imshow(mask, cmap="gray", interpolation='nearest', vmin=-pp, vmax=pp*2)
    plt.colorbar(shrink=0.8, fraction=0.1)


   

    plt.subplot(438)
    mask = np.ma.masked_equal(diff, 0)
    mask[mask > 0] = 0
    small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
    w, h = small_image.shape
    image_array = small_image.reshape(-1, 1)
    dbscan = DBSCAN(eps=0.6, min_samples=50).fit(image_array)
    labels = dbscan.labels_
    segmented_image = labels.reshape(w, h)
    segmented_image[segmented_image!=-1] = 0
    segmented_image[segmented_image == -1] = 1
    m_segmented_image = segmented_image.copy()
    plt.imshow(m_segmented_image, cmap='viridis')


    plt.subplot(439)
    mask = np.ma.masked_equal(diff, 0)
    small_image = resize(mask, (mask.shape[0] // 2, mask.shape[1] // 2))
    w, h = small_image.shape
    image_array = small_image.reshape(-1, 1)
    dbscan = DBSCAN(eps=0.2, min_samples=100).fit(image_array)
    labels = dbscan.labels_
    segmented_image = labels.reshape(w, h)
    segmented_image[segmented_image != -1] = 0
    segmented_image[segmented_image == -1] = 1
    d_segmented_image = segmented_image.copy()
    plt.imshow(d_segmented_image, cmap='viridis')

    plt.subplot(4, 3, 10)
    # Извлечение координат пикселей, имеющих значение 1
    coords = np.column_stack(np.where(m_segmented_image == 1))

    dbscan = DBSCAN(eps=15., min_samples=50).fit(coords)
    labels = dbscan.labels_

    plt.imshow(m_segmented_image, cmap='viridis')

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f'Количество кластеров: {n_clusters}')
    print(f'Количество шумовых точек: {n_noise}')

    # Визуализация результатов (опционально)
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Черный цвет для шума
            col = [0, 0, 0, 1]

        class_member_mask = (labels == k)

        xy = coords[class_member_mask]
        plt.plot(xy[:, 1], xy[:, 0], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=2)



    plt.subplot(4, 3, 11)

    mask = np.ma.masked_equal(diff, 0)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)

    unique_labels = set(labels)
    unique_labels.discard(-1)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    for k, col in zip(unique_labels, colors):

        class_member_mask = (labels == k)

        xy = coords[class_member_mask]
        plt.plot(xy[:, 1]*2, xy[:, 0]*2, 'o', markerfacecolor=tuple(col),
                 markeredgewidth=0, markersize=2)


    plt.subplot(4, 3, 12)
    # Извлечение координат пикселей, имеющих значение 1
    coords = np.column_stack(np.where(d_segmented_image == 1))

    dbscan = DBSCAN(eps=eps_l, min_samples=min_samples_l).fit(coords)
    labels = dbscan.labels_

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f'Количество кластеров: {n_clusters}')
    print(f'Количество шумовых точек: {n_noise}')

    mask = np.ma.masked_equal(diff, 0)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)

    unique_labels = set(labels)
    unique_labels.discard(-1)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    for k, col in zip(unique_labels, colors):
        class_member_mask = (labels == k)

        xy = coords[class_member_mask]
        plt.plot(xy[:, 1] * 2, xy[:, 0] * 2, 'o', markerfacecolor=tuple(col),
                 markeredgewidth=0, markersize=2)



    plt.show()


    unique_labels = set(labels)
    unique_labels.discard(-1)  # Удаляем метку шума

    plt.figure(figsize=(8, 8))

    mask = np.ma.masked_equal(diff, 0)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar(shrink=0.8, fraction=0.1)
    # Список для хранения центров кластеров и их прямоугольников
    cluster_centers = []
    rectangles = []


    for k in unique_labels:
        class_member_mask = (labels == k)
        xy = coords[class_member_mask]

        # Вычисляем центр кластера
        center = xy.mean(axis=0)*2
        cluster_centers.append(center)

        # Вычисляем координаты прямоугольника
        min_coords = xy.min(axis=0)*2
        max_coords = xy.max(axis=0)*2

        # Вычисляем площадь прямоугольника
        area = (max_coords[0] - min_coords[0]) * (max_coords[1] - min_coords[1])
        print(area)
        if min_area_threshold <= area <= max_area_threshold:
            rectangles.append((min_coords, max_coords))


    # Отображаем прямоугольники, описывающие кластеры
    ax = plt.gca()
    for min_coords, max_coords in rectangles:
        rect = patches.Rectangle((min_coords[1], min_coords[0]), max_coords[1] - min_coords[1],
                                 max_coords[0] - min_coords[0],
                                 linewidth=2, edgecolor='blue', facecolor='none')
        ax.add_patch(rect)


    # Отображаем центры кластеров
    for center in cluster_centers:
        plt.plot(center[1], center[0], 'o', markerfacecolor='green', markeredgewidth=0, markersize=5)

    plt.title(f'{info.get_datetime()} - {info1.get_datetime()}')
    plt.show()


