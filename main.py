from scipy.interpolate import interp2d, RegularGridInterpolator

from src import graphics
from src import file
from src import GUI
from src import logics
from skimage.measure import label, regionprops
import os

import cv2
import numpy as np

import matplotlib.pyplot as plt

from src.graphics import auto_contrast_skimage

file_number = 150

current_directory = os.getcwd()

path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")

#path = os.path.join(current_directory, "data", "KEO", "2014", "30")

path = os.path.join(current_directory, "data", "KEO", "20130417")

#path = os.path.join(current_directory, "data", "KEO", "20130416")
# "data.ASI0.2023.10.11.5577"
# name="data.ASI0.2024.01.12.5577", name_file="data.ASI0.2024.01.12.5577"
# path = os.path.join(current_directory, "data", "ASI0", "2024", "01", "12")
new_path = os.path.join(path, "5577")

new_path = path

names = file.get_name_file(new_path)

#
# logics.create_video(names, new_path, start_i=0, flag_info=True, names=True, name_file="data.KEO.2014.30.heatmap.hists",
#                     name="data.KEO.2014.30.heatmap.hists", cut=True, save_folder="result/KEO/2014/30", save_img=True,
#                     dark=False, fit_format="2014", _zip=False, hists=True, name_img_folder="img_for_video/hists")
#
# logics.create_video(names, new_path, start_i=0, flag_info=True, names=True, name_file="data.KEO.2014.30.heatmap",
#                     name="data.KEO.2014.30.heatmap", cut=True, save_folder="result/KEO/2014/30", save_img=True,
#                     dark=False, fit_format="2014", _zip=False, hists=False, name_img_folder="img_for_video/base")

#
name_path = os.path.join(new_path, names[22])
info, data = file.open_gz(name_path, _zip=False)

data[300, 250] = 60000



data_copy, label_diff_region, data_copy_del = graphics.remove_single_pixels(data, True, True, True)


plt.subplot(231)
plt.imshow(data, cmap="gray")
plt.subplot(232)
plt.imshow(graphics.cut_img(data_copy_del), cmap="gray")
plt.subplot(233)
plt.imshow(graphics.cut_img(data_copy), cmap="gray")

plt.subplot(234)
# plt.imshow(cut_diff, cmap="gray")
plt.hist(graphics.cut_img(data).flatten(), bins=2000)
plt.xlim(xmin=0, xmax=10000)

plt.subplot(235)
# plt.imshow(cut1_diff, cmap="gray")
plt.hist(graphics.cut_img(data_copy).flatten(), bins=2000)
plt.xlim(xmin=0, xmax=10000)

plt.subplot(236)
plt.imshow(label_diff_region)

plt.show()

# graphics.print_graphics_cv2_arr(data, data_copy, data.max())

#logics.viewing_pictures(names, file_number, new_path, dark=False, _zip=False)


#
# plt.subplot(221)
# plt.imshow(data, cmap="gray")
# plt.subplot(222)
# plt.imshow(blurred_image, cmap="gray")
# plt.subplot(223)
# plt.imshow(cut_diff, cmap="gray")
# plt.subplot(224)
# plt.imshow(cut1_diff, cmap="gray")
# plt.show()


# data_c = data.copy()
# c = 0
# for i in range(label_diff.max()):
#     #if np.count_nonzero(label_diff == i) == 1:
#     if np.sum((label_diff == i) & (~np.isnan(label_diff))) == 1:
#         indices = np.where(label_diff == i)
#         #print(indices[0], indices[1])
#         data_c[indices[0], indices[1]] = (data[indices[0]-1, indices[1]] + data[indices[0], indices[1]-1] +
#                                         data[indices[0]+1, indices[1]] + data[indices[0], indices[1]+1])/4
#         # label_diff_c = label_diff.copy()
#         # label_diff_c[label_diff_c != i] = 0
#         # plt.imshow(label_diff_c)
#         # plt.show()
#         c += 1


#
# plt.subplot(141)
# plt.imshow(data, cmap="gray")
# plt.subplot(142)
# plt.imshow(data_c, cmap="gray")
# plt.subplot(143)
# plt.imshow(blurred_image, cmap="gray")
# plt.subplot(144)
# plt.imshow(diff)
# plt.show()


#
# dark1, time1 = logics.get_dark_AVG(names, new_path)
# dark2, time2 = logics.get_dark_AVG(np.flip(names), new_path)
#
#
# name_path = os.path.join(new_path, names[70])
# info, data = file.open_gz(name_path)
#
#
#
# time = file.FitsInfo(info).get_datetime()
# data = logics.subtract_noise_frame(dark1, dark2, time1, time2, data, time)
# data = (data - data.min()) / (data.max() - data.min())
# data = (data * 10000).astype(int)
#
# data = graphics.cut_img(data)
# data, _, _ = auto_contrast_skimage(data)
# data_orig = data.astype(float)
# data = data_orig.copy()
#

# from photutils.background import Background2D, MedianBackground
# bkg_estimator = MedianBackground()
# bkg = Background2D(data, (50, 50), filter_size=(3, 3),
#                    bkg_estimator=bkg_estimator)
# data = data.astype(np.float64)
# data -= bkg.background  # subtract the background
#
# threshold = 1.5 * bkg.background_rms
#
# from astropy.convolution import convolve
# from photutils.segmentation import make_2dgaussian_kernel
# kernel = make_2dgaussian_kernel(3.0, size=5)  # FWHM = 3.0
# convolved_data = convolve(data, kernel)
#
# from photutils.segmentation import detect_sources
# segment_map = detect_sources(convolved_data, threshold, npixels=10)
#
# import numpy as np
# import matplotlib.pyplot as plt
# from astropy.visualization import SqrtStretch
# from astropy.visualization.mpl_normalize import ImageNormalize
# norm = ImageNormalize(stretch=SqrtStretch())
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12.5))
# ax1.imshow(data, origin='lower', cmap='Greys_r', norm=norm)
# ax1.set_title('Background-subtracted Data')
# ax2.imshow(segment_map, origin='lower', cmap=segment_map.cmap,
#            interpolation='nearest')
# ax2.set_title('Segmentation Image')
#
# plt.show()

# print(names[0])
# name_path = os.path.join(new_path, names[0])
# info, data = file.open_gz(name_path)


#
# name_path = os.path.join(new_path, names[1])
# info, data1 = file.open_gz(name_path)
#
# name_path = os.path.join(new_path, names[2])
# info, data2 = file.open_gz(name_path)
#
# avg = np.mean([data, data1, data2], axis=0)
# print(avg)


# print(names)

# bins = np.linspace(0, 10000, 101)
#bins = np.append(bins, 70000)
# print(bins)





# save_folder="result/ASI0/2023/10/11/5577"
# title = "data.ASI0.2023.10.11.5577.viridis.100bins_limit_10000_0"
#"ASI0.2023.10.11.5577.viridis_auto_contrast_edges.15"
# logics.create_heatmap(names, new_path, bins=100, edges=5, log_info=True, auto_contrast=False,
#                       title="KEO.20130417.viridis_edges_5_limit_5000",
#                       limit=5000, cmap='viridis', save_folder="result/KEO/20130417", fit_format="2014", zip=False)

# graphics.print_graphics_cv2(combined_image, combined_image.max())

#GUI.start()


# input_string = r"C:\\work\\search_for_oxide_cloud\\SfOC/gggg.png"
#
# # Преобразование строки в путь
# path = os.path.normpath(input_string)
#
# print(path)


# result = create_img_for_video(names, 13, 14, name="GG", cut=True, names=True)
# plt.imshow(result[0])
# plt.show()
#name_file="data.ASI0.2023.10.11.5577.heatmap.test_1
#"data.KEO.2014.30.heatmap",
#"data.KEO.20130417.heatmap"


#
# name_path = os.path.join(new_path, names[20])
# info, data = file.open_gz(name_path, _zip=False)
#
# name_path1 = os.path.join(new_path, names[21])
# info1, data1 = file.open_gz(name_path1, _zip=False)
#
# data_c = graphics.cut_img(data, nan=True)
# data1_c = graphics.cut_img(data1, nan=True)
#
# diff1 = data_c - data1_c
#
# name_path = os.path.join(new_path, names[21])
# _, data = file.open_gz(name_path, _zip=False)
#
# name_path1 = os.path.join(new_path, names[22])
# _, data1 = file.open_gz(name_path1, _zip=False)
#
# data_c = graphics.cut_img(data, nan=True)
# data1_c = graphics.cut_img(data1, nan=True)
# diff = data_c - data1_c
#
#
# graphics.create_hists(data_c, data1_c, diff, diff1, show=True)

# import joypy
#
# import pandas as pd
# import numpy as np
# from matplotlib import pyplot as plt
# from matplotlib import cm
#
#
# temp = pd.read_csv("data/daily_temp.csv",comment="%")
#
# labels=[y if y%10==0 else None for y in list(temp.Year.unique())]
# fig, axes = joypy.joyplot(temp, by="Year", column="Anomaly", labels=labels, range_style='own',
#                           grid="y", linewidth=1, legend=False, figsize=(6,5),
#                           title="Global daily temperature 1880-2014 \n(°C above 1950-80 average)",
#                           colormap=cm.autumn_r)
#
# plt.show()


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
