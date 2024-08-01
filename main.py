import time



from src import clustering
from src import graphics
from src import file
import os

import cv2
import numpy as np

import matplotlib.pyplot as plt
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
name = "SLIC_DBSCAN_RGB"

# buf, labels, img, info, info1 = clustering.SLIC_DBSCAN(names_files=names, new_path=new_path, i=i, return_img=True, all_info=True,
#                                               save_folder=f"C:\\Users\\nech14\\Desktop", nameFile=f"{i}")

# clustering.print_SLIC_DBSCAN(names_files=names, new_path=new_path, i=i)

# for i in range(len(names)-1):
#     data, data1, diff, info, info1 = clustering.work_with_date(names, new_path, i, percent_to_trim=0.1,
#                                                     _zip=False, type_fits=file.FitsInfo2014)
#
#
#     diff = data.astype(float) - data1.astype(float)
#     print(f"{i}/{len(names)-1}")
#
#     graphics.save_heat_map(diff, save_folder=save_folder, nameFile=i, color_bar=False)


start_i = 0
end_i = len(names)-1
for i in range(start_i, end_i):
    image_file = os.path.join(image_folder, f"{i}.png")
    buf, labels, img = clustering.SLIC_DBSCAN(names_files=names, new_path=new_path, i=i, return_img=True, all_info=False,
    # buf, labels, img, info, info1 = clustering.SLIC_DBSCAN(names_files=names, new_path=new_path, i=i, return_img=True, all_info=False,
                                                           save_folder=save_folder+"\\slic_dbscan_RGB", nameFile=f"{i}", image_file=image_file,
                                                           suptitle=f"Frame {i}")

    # plt.imshow(img)
    # plt.show()
    # print(buf, info.get_norm_time(), info1.get_norm_time())

    print(f"{i}/{end_i}")
    # print(name_info)
    # Открытие файла в режиме добавления (append)
    with open(f"{save_folder}\\count_{name}.txt", "a", encoding="utf-8") as file:
        # Запись дополнительного текста в файл
        # file.write(f"{len(buf)}   {info.get_norm_time()}   {info1.get_norm_time()}   {i}   {i+1}\n")
        file.write(f"{len(buf)}   {i}   {i+1}\n")

    # Засеките время окончания
end_time = time.time()
with open(f"{save_folder}\\count_{name}.txt", "a", encoding="utf-8") as file:
    # Запись дополнительного текста в файл
    file.write(f"{end_time}\n")



#

start_time = time.time()

# for i in range(len(names)-8):
# for i in range(0, len(names)-7):
save_folder = "C:\\work\\search_for_oxide_cloud\\SfOC\\result\\KEO\\2014\\28\\test"
start_i = 0
end_i = len(names)-7

#
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
#

#
# # Рассчитайте и выведите длительность выполнения
# execution_time = end_time - start_time
# print(f"Длительность выполнения программы: {execution_time:.2f} секунд")


# clustering.base_lvl(names, new_path)
#print(clustering.get_clusters(names, new_path, 123))

def logfun(text, i, n):
    print(f"{text}: {i}/{n}")

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





def test_matrix(path_file = 'C:/work/search_for_oxide_cloud/ALL SKY IMAGERS/Calibration SN10210/UNIFORMITY COEFFICIENT FILES/client_test_unifmap_1024x320.dat'):
    test0 = np.fromfile(path_file, dtype='float32')
    print(test0)

    test0 = np.reshape(test0, (1024, 320), order='F')
    print(test0[0, 0])
    print(test0[0, 319])
    print(test0[1023, 0])
    print(test0[1023, 319])



# logics.viewing_pictures(names, file_number, new_path, dark=False, _zip=False)



#GUI.start()




def hist_3d(names, file_number, end=10, name_g="", xlim3d_min=0, xlim3d_max=None, ylim3d_min=0, ylim3d_max=None,
            rotate=False, x_agnes_end=130, y_agnes_end=90, start_folder="result", save_folder="img"):
    # histogram = plt.hist(data_cut.flatten(), bins='auto')
    # print(histogram)
    # plt.show()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection="3d")
    my_cmap = plt.cm.inferno

    count_files = len(names) - end

    for i in range(file_number, count_files):
        # we create evenly spaced bins between the minimum and maximum of the entire dataframe
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path)
        data_cut = graphics.cut_img(data)

        # non_zero_data_cut = data_cut[data_cut != 0]

        histvals, _ = np.histogram(data_cut.flatten(), bins="auto")
        histvals = histvals[1:]

        xbins = np.linspace(data_cut.flatten().min().min(), data_cut.flatten().max().max(), len(histvals) + 1)
        # and calculate the center and widths of the bars
        xcenter = np.convolve(xbins, np.ones(2), "valid") / 2
        xwidth = np.diff(xbins)

        # print(xbins)
        # print(xcenter)

        ax.bar(left=xcenter, height=histvals, width=xwidth, zs=(i - file_number) / 100, zdir="y", alpha=0.666,
               linewidth=0.3, color=my_cmap((i - file_number) / (count_files - file_number)))

        print(f"{i - file_number}/{count_files - file_number}")

    ax.set_xlabel("value")
    ax.set_ylabel("column")
    ax.set_zlabel("count")

    # label every other column number
    if not ylim3d_max is None:
        ax.set_ylim3d(ylim3d_max, ylim3d_min)
    if not xlim3d_max is None:
        ax.set_xlim3d(xlim3d_min, xlim3d_max)

    plt.title(name_g)

    if rotate:
        if not os.path.exists(start_folder + '/' + save_folder):
            # Если не существует, создаем папку
            os.makedirs(start_folder + '/' + save_folder)
        for angle in range(0, x_agnes_end):
            ax.view_init(0, angle)
            print(f"rotate_x: {angle}/{x_agnes_end}")
            # plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle) + '.png')
            # plt.pause(.001)

        for angle in range(0, y_agnes_end):
            ax.view_init(angle, x_agnes_end)
            print(f"rotate_y: {angle}/{y_agnes_end}")
            # plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle + x_agnes_end) + '.png')
            # plt.pause(.001)

    # plt.show()


def hist_3d_diff(names, file_number, end=10, name_g="", xlim3d_min=0, xlim3d_max=None, ylim3d_min=0, ylim3d_max=None,
                 rotate=False, x_agnes_end=130, y_agnes_end=90, start_folder="result", save_folder="diff"):
    # histogram = plt.hist(data_cut.flatten(), bins='auto')
    # print(histogram)
    # plt.show()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection="3d")
    my_cmap = plt.cm.inferno

    count_files = len(names) - end - 1

    for i in range(file_number, count_files):
        # we create evenly spaced bins between the minimum and maximum of the entire dataframe
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path)
        data_cut = graphics.cut_img(data)

        name_path1 = os.path.join(new_path, names[i + 1])
        info1, data1 = file.open_gz(name_path1)
        data_cut1 = graphics.cut_img(data1)

        h_diff = data_cut.astype(float) - data_cut1.astype(float)
        # non_zero_data_cut = data_cut[data_cut != 0]

        h_diff = h_diff[h_diff != 0]

        histvals, _ = np.histogram(h_diff.flatten(), bins="auto")
        histvals = histvals[1:]

        xbins = np.linspace(data_cut.flatten().min().min(), data_cut.flatten().max().max(), len(histvals) + 1)
        # and calculate the center and widths of the bars
        xcenter = np.convolve(xbins, np.ones(2), "valid") / 2
        xwidth = np.diff(xbins)

        # print(xbins)
        # print(xcenter)

        ax.bar(left=xcenter, height=histvals, width=xwidth, zs=(i - file_number) / 100, zdir="y", alpha=0.666,
               linewidth=0.3, color=my_cmap((i - file_number) / (count_files - file_number)))

        print(f"{i - file_number}/{count_files - file_number}")

    ax.set_xlabel("value")
    ax.set_ylabel("column")
    ax.set_zlabel("count")

    # label every other column number
    if not ylim3d_max is None:
        ax.set_ylim3d(ylim3d_max, ylim3d_min)
    if not xlim3d_max is None:
        ax.set_xlim3d(xlim3d_min, xlim3d_max)

    plt.title(name_g)

    if rotate:
        if not os.path.exists(start_folder + '/' + save_folder):
            # Если не существует, создаем папку
            os.makedirs(start_folder + '/' + save_folder)
        for angle in range(0, x_agnes_end):
            ax.view_init(0, angle)
            print(f"rotate_x: {angle}/{x_agnes_end}")
            # plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle) + '.png')
            # plt.pause(.001)

        for angle in range(0, y_agnes_end):
            ax.view_init(angle, x_agnes_end)
            print(f"rotate_y: {angle}/{y_agnes_end}")
            # plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle + x_agnes_end) + '.png')
            # plt.pause(.001)

    # plt.show()


def create_video_hist_3d(name_file=None, folder_name="result/ASI0/2023/10/11/OH1", save_folder='video'):
    if name_file is None:
        name_file = folder_name

    if not os.path.exists(folder_name + '/' + save_folder):
        # Если не существует, создаем папку
        os.makedirs(folder_name + '/../' + save_folder)

    # Размеры кадра и частота кадров в видео
    date1 = plt.imread(folder_name + f'/rotanim_{0}.png')
    frame_width = date1.shape[1]
    frame_height = date1.shape[0]
    fps = 5
    # Создаем объект VideoWriter для записи видео в формате MP4
    fourcc1 = cv2.VideoWriter_fourcc(*'mp4v')
    out1 = cv2.VideoWriter(folder_name + '/../' + save_folder + '/' + name_file + ".mp4", fourcc1, fps,
                           (frame_width, frame_height))

    count = 0
    for i in range(1, 220):
        frame = cv2.imread(folder_name + f'/rotanim_{i}.png')
        out1.write(frame)
        if True:
            count += 1
            print(f"create video: {count}/221")

    # Закрываем объект VideoWriter
    out1.release()


# hist_3d(names, file_number, len(names)-20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=0.5, rotate=True)
# hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=1.5, rotate=True)
# hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.OH", xlim3d_max=20000, ylim3d_max=(len(names)-file_number-20)//100, rotate=True, start_folder="result/ASI0/2023/10/11/OH")


# hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=(len(names)-file_number)/100, rotate=True, start_folder="result/ASI0/2023/10/11/5577")

# create_video_hist_3d(name_file="result_ASI0_2023_10_11_OH", folder_name="result/ASI0/2023/10/11/OH/img")


# hist_3d_diff(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577.diff", ylim3d_max=(len(names)-file_number)/100, rotate=True, start_folder="result/ASI0/2023/10/11/5577")

# create_video_hist_3d(name_file="result_ASI0_2023_10_11_5577_diff", folder_name="result/ASI0/2023/10/11/5577/diff")

print('hay')
