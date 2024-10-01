import time

from SfOC.src.logging.logging import log_operation
from src import clustering
from src import graphics
from src import file
from SfOC.src.logics import write_data_in_file
from SfOC.src.logics import save_heat_map

import os

import cv2
import numpy as np

import matplotlib.pyplot as plt
from SfOC.src.logging import base_log
from skimage.transform import resize
from scipy.interpolate import griddata
from src.graphics import auto_contrast_skimage
from skimage import color
from skimage.segmentation import slic, mark_boundaries
from skimage.util import img_as_float
from skimage import io
import argparse

from sklearn.cluster import DBSCAN


file_number = 150

current_directory = os.getcwd()

path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")

# path = os.path.join(current_directory, "data", "KEO", "2014", "30")
# path = os.path.join(current_directory, "data", "KEO", "2014", "28")

path = os.path.join(current_directory, "data", "KEO", "20130417")
# path = os.path.join(current_directory, "data", "andor", "20240504")

# path = os.path.join(current_directory, "data", "KEO", "20130416")
# "data.ASI0.2023.10.11.5577"
# name="data.ASI0.2024.01.12.5577", name_file="data.ASI0.2024.01.12.5577"
# path = os.path.join(current_directory, "data", "ASI0", "2024", "01", "12")
new_path = os.path.join(path, "5577")

new_path = path

names = file.get_name_file(new_path)

# clustering.model_method_frames(new_path=new_path, names_files=names)
# clustering.start(new_path=new_path, names_files=names, start=120, end=127)
# clustering.start(new_path=new_path, names_files=names, start=120, end=127)
# clustering.model_method_frame_GaussianMixture(new_path=new_path, names_files=names)
# clustering.model_method_frames_GaussianMixture(names, new_path, start=19, end=19+7, log=True)

# _zip = False
# names_files = names
# i = 123
# diff1 = None
# name = "ggg"
# percent_to_trim = 0.1
#
# name_path = os.path.join(new_path, names_files[i])
# info, data = file.open_gz(name_path, _zip=_zip)
#
# name_path1 = os.path.join(new_path, names_files[i + 1])
# info1, data1 = file.open_gz(name_path1, _zip=_zip)
#
#
# data = graphics.cut_img(data, percent_to_trim)
# data1 = graphics.cut_img(data1, percent_to_trim)
#
# img = graphics.create_img_for_video(data, data1, name=name)
#
#
# diff = data - data1
# print(graphics.get_hist_p(data, data1, diff))

# print(logics.get_hist_p(names_files=names, new_path=new_path, start_i=20, end_i=200, counts_checks=4))

#
# clustering.bin_frame(names_files=names, new_path=new_path, i=358, type_print=clustering.BinShow.ALL,
#                      eps=1.2, min_samples=128//2)

# # поиск лучших значений дли бинаризации
# clustering.bin_frame_best(names_files=names, new_path=new_path, i=119, eps_steep=0.5, min_samples_steep=10,
#                           rows=6, cols=6, eps_steep_start=0., min_samples_start_steep=0, save_folder=f"C:\\Users\\nech14\\Desktop", nameFile="30_N_1")
#
# clustering.bin_frame_best(names_files=names, new_path=new_path, i=119, eps_steep=0.2, min_samples_steep=5,
#                           rows=6, cols=6, eps_steep_start=0.8, min_samples_start_steep=35, save_folder=f"C:\\Users\\nech14\\Desktop", nameFile="30_N_2")

#
# # Чтение изображения
# image = cv2.imread('C:\\Users\\nech14\\Downloads\\Telegram Desktop\\Lenna.png')
#
# # Преобразование изображения в оттенки серого
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
# clustered_image, diff = clustering.canny_frame(names_files=names, new_path=new_path, i=123,
#                                                eps=50, min_samples=10, return_diff=True)
#
# # Отображение результатов
# plt.figure(figsize=(15, 5))
#
# plt.subplot(1, 2, 1)
# plt.title("Оригинальное изображение")
# pp= 500
# plt.imshow(diff, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
# # plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
# plt.axis('off')
#
#
# plt.subplot(1, 2, 2)
# plt.title("Контуры, выделенные DBSCAN")
# plt.imshow(clustered_image, cmap='gray')
# plt.axis('off')
#
# plt.tight_layout()
# plt.show()


# clustering.canny_frame_best(names_files=names, new_path=new_path, i=123, eps_steep=0.5, min_samples_steep=10, log=True, cmap="gray",
#                             rows=6, cols=6, eps_steep_start=0., min_samples_start_steep=0, save_folder=f"C:\\Users\\nech14\\Desktop", nameFile="canny_30_g_1")
#
# clustering.canny_frame_best(names_files=names, new_path=new_path, i=123, eps_steep=5, min_samples_steep=5, log=True, cmap="gray",
#                             rows=6, cols=6, eps_steep_start=0., min_samples_start_steep=0, save_folder=f"C:\\Users\\nech14\\Desktop", nameFile="canny_30_g_2")
#
# clustering.canny_frame_best(names_files=names, new_path=new_path, i=123, eps_steep=10, min_samples_steep=5, log=True, cmap="gray",
#                             rows=6, cols=6, eps_steep_start=0., min_samples_start_steep=0, save_folder=f"C:\\Users\\nech14\\Desktop", nameFile="canny_30_g_3")
#
#

# i=123
i = 358
# i = 21

# clustering.print_canny_with_bin(names, new_path, i, save_folder=f"C:\\Users\\nech14\\Desktop", nameFile="canny_with_bin_30",
#                                 suptitle="KEO 20130417")

start_time = time.time()

save_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\2014\\28\\test"
save_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\20130417"
image_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\20130417\\diff"
# save_folder = None



save_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\2014\\28\\test"




image_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\2014\\28\\diff1"
save_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\2014\\28\\test_test"
save_cluster_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\2014\\28\\test_test\\clusters"


name_data = "ASI1\\2024\\03"
# name_data = "KEO\\2014"
# name_data = "KEO"
filter_d = "5577"
# filter_d = "6300"
# filter_d = None
path = os.path.join(current_directory, "data", name_data)

save_folder_b = "C:\\data2"
logs = True

fit_format = file.FitsInfo
# fit_format = file.FitsInfo2014
_zip = True
# _zip = False
# name = "SLIC_DBSCAN_RGB"

start_i = 20
end_i = 25

n_p = np.array(["03", "04", "05"])
# n_p = np.array(["30"])
# n_p = np.array(["20130417"])

eps = 0.025

log_fun = base_log


for n in n_p:

    if not filter_d is None:
        new_path = os.path.join(path, n, filter_d)
        save_folder = os.path.join(save_folder_b, name_data, n, filter_d)
    else:
        new_path = os.path.join(path, n)
        save_folder = os.path.join(save_folder_b, name_data, n)
    image_folder = os.path.join(save_folder, "image_diff")
    # image_folder = None
    save_cluster_folder = os.path.join(save_folder, "clusters")
    save_folder_slic = os.path.join(save_folder, "slic")
    # save_folder_slic = None
    names = file.get_name_file(new_path)


    save_heat_map(names, new_path, image_folder, logs=logs, start_i=start_i, end_i=end_i, _zip=_zip,
                  type_fits=fit_format, log_fun=log_fun)
    write_data_in_file(names, new_path, save_folder, image_folder=image_folder, save_folder_clusters=save_cluster_folder,
                       logs=logs, start_i=start_i, end_i=end_i, type_fits=fit_format, _zip=_zip,
                       save_folder_slic =save_folder_slic, eps=eps, log_fun=log_fun)



#
# name = "GM"
# for i in range(start_i, end_i):
#     # optimal_n_components, name_info = clustering.start(names, new_path, save_folder, i, i+7, log=True)
#     # optimal_n_components, name_info = clustering.model_method_frames(names, new_path, save_folder, i, i+7, log=True)
#     optimal_n_components, name_info = clustering.model_method_frames_GaussianMixture(names, new_path, save_folder, i, i+7, log=True)
#     print(f"{i}/{end_i}")
#     # print(name_info)
#     # Открытие файла в режиме добавления (append)
#     with open(f"{save_folder}\\count_{name}.txt", "a", encoding="utf-8") as file:
#         # Запись дополнительного текста в файл
#         file.write(f"{optimal_n_components}   {name_info[0]}   {name_info[-1]}   {i}   {i+7}\n")
# # Засеките время окончания
# end_time = time.time()
# with open(f"{save_folder}\\count_{name}.txt", "a", encoding="utf-8") as file:
#     # Запись дополнительного текста в файл
#     file.write(f"{end_time}\n")
#


# clustering.base_lvl(names, new_path)
#print(clustering.get_clusters(names, new_path, 123))

# path_file_matrix="C:/work/search_for_oxide_cloud/ALL SKY IMAGERS/Calibration SN10210/UNIFORMITY COEFFICIENT FILES/20190718_Russia-LZOS_KEO10210_5577L14002-02_0001000ms_G3_FOV180_uniformity_map_2048x2048.dat"
#
# logics.create_video(names, new_path, start_i=0, flag_info=True, names=True, name_file="data.ASI0.2023.10.11.5577.heatmap.hists.remove_single_pixels.correct_matrix.Rayleigh1",
#                     name="data.ASI0.2023.10.11.5577.heatmap.hists", cut=True, save_folder="result/ASI0/2023/10/11/5577", save_img=True,
#                     dark=False, fit_format=None, _zip=True, hists=True, name_img_folder="img_for_video/hists_mod1",
#                     remove_single_pixels=True, correct_matrix=path_file_matrix, Rayleigh=True)
#
# logics.create_video(names, new_path, start_i=60, end_i=80, flag_info=True, names=True, name_file="data.ASI0.2023.10.11.5577.heatmap.hists.remove_single_pixels.correct_matrix.Rayleigh3",
#                     name="data.KEO.2023.10.11.5577.heatmap.hists.remove_single_pixels.correct_matrix.Rayleigh", cut=True, save_folder="result/ASI0/2023/10/11/5577/test", save_img=True,
#                     dark=True, fit_format=file.FitsInfo, _zip=True, hists=True, name_img_folder="img_for_video/hists_mod3",
#                     remove_single_pixels=True, correct_matrix=path_file_matrix, Rayleigh=True, logfun=None, frames_s=10,
#                     counts_checks=3, check_frame=[63, 75])




# logics.create_video(names, new_path, start_i=4, flag_info=True, names=True, name_file="data.andor.20240504.heatmap.hist",
#                     name="data.andor.20240504.heatmap.hist", cut=True, save_folder="result/andor/20240504", save_img=True,
#                     dark=False, dark_name=None, fit_format=file.FitsInfoAndor, _zip=False, hists=True, name_img_folder="img_for_video/hist")

# logics.create_video(names, new_path, start_i=4, flag_info=True, names=True, name_file="data.andor.20240506.heatmap.hist",
#                     name="data.andor.20240506.heatmap.hist", cut=True, save_folder="result/andor/20240506", save_img=True,
#                     dark=False, dark_name=None, fit_format="andor", _zip=False, hists=True, name_img_folder="img_for_video/hist")
#
# logics.create_video(names, new_path, start_i=20, end_i=50, flag_info=True, names=True, name_file="data.andor.20240504.heatmap.hist",
#                     name="data.andor.20240504.heatmap.hist.remove_single_pixels.Rayleigh", cut=True, save_folder="result/andor/20240504/test", save_img=True,
#                     dark=False, fit_format=file.FitsInfoAndor, _zip=False, hists=True, name_img_folder="img_for_video/hists_mod",
#                     remove_single_pixels=True, correct_matrix=None, Rayleigh=False, logfun=None, frames_s=2, data_index=0)



# logics.viewing_pictures(names, file_number, new_path, dark=False, _zip=False)



#GUI.start()






# hist_3d(names, file_number, len(names)-20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=0.5, rotate=True)
# hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=1.5, rotate=True)
# hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.OH", xlim3d_max=20000, ylim3d_max=(len(names)-file_number-20)//100, rotate=True, start_folder="result/ASI0/2023/10/11/OH")


# hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=(len(names)-file_number)/100, rotate=True, start_folder="result/ASI0/2023/10/11/5577")

# create_video_hist_3d(name_file="result_ASI0_2023_10_11_OH", folder_name="result/ASI0/2023/10/11/OH/img")


# hist_3d_diff(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577.diff", ylim3d_max=(len(names)-file_number)/100, rotate=True, start_folder="result/ASI0/2023/10/11/5577")

# create_video_hist_3d(name_file="result_ASI0_2023_10_11_5577_diff", folder_name="result/ASI0/2023/10/11/5577/diff")

print('hay')
