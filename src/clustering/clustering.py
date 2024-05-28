import os

import numpy as np

from SfOC.src import graphics, file
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, OPTICS
from sklearn.neighbors import NearestNeighbors
from skimage.transform import resize
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.patches as patches
from scipy.signal import argrelextrema


def start():
    pass

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


