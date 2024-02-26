from src import graphics
from src import file
import os

import cv2
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

file_number = 11


def create_all_png(frequency="5577"):
    current_directory = os.getcwd()

    path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")
    new_path = os.path.join(path, frequency)

    names = file.get_name_file(new_path)

    save_path = os.path.join(path, frequency + "_img")
    for name in names:
        name_path = os.path.join(new_path, name)
        data = file.open_gz(name_path)

        graphics.save_graphics(data, save_path, name[:-8])
        # graphics.print_graphics(data)
        print(name)


def create_mp4(dates, name="output", flag_info=False):
    # Размеры кадра и частота кадров в видео
    date = dates[0]
    frame_width = date.shape[1]
    frame_height = date.shape[0]
    fps = 1
    print(date.shape)
    # Создаем объект VideoWriter для записи видео в формате MP4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(name + ".mp4", fourcc, fps, (frame_width, frame_height), isColor=False)

    count = 0
    for i in dates:
        out.write(i)
        if flag_info:
            count += 1
            print(f"create video: {count}/{len(dates)}")

    # Закрываем объект VideoWriter
    out.release()


def create_img_for_video(names_files, start_i, end_i, flag_info=False, name=None, cut=False,
                         percent_to_trim=0.1, names=False):
    datas = []
    for i in range(start_i, end_i):
        name_path = os.path.join(new_path, names_files[i])
        info, data = file.open_gz(name_path)

        name_path1 = os.path.join(new_path, names_files[i + 1])
        info1, data1 = file.open_gz(name_path1)

        if cut:
            data_cut = graphics.cut_img(data, percent_to_trim)
            data1_cut = graphics.cut_img(data1, percent_to_trim)
            if names:
                info_f = file.FitsInfo(info)
                info_f1 = file.FitsInfo(info1)
                img = graphics.create_img_for_video(data_cut, data1_cut, name=name,
                                                    names=[info_f.get_norm_time(), info_f1.get_norm_time()])
            else:
                img = graphics.create_img_for_video(data_cut, data1_cut, name=name)
        else:
            if names:
                info_f = file.FitsInfo(info)
                info_f1 = file.FitsInfo(info1)
                img = graphics.create_img_for_video(data, data1, name=name,
                                                    names=[info_f.get_norm_time(), info_f1.get_norm_time()])
            else:
                img = graphics.create_img_for_video(data, data1, name=name)
        # plt.imshow(img)
        # plt.show()
        datas.append(img)
        if flag_info:
            print(f"create img: {(i - start_i)}/{end_i - start_i - 1}")
    return datas


def create_video(names_files, start_i=6, end_i=None, name_file="output", flag_info=False, name=None, cut=False,
                 names=False):
    if end_i is None:
        end_i = len(names_files) - 2
    datas = create_img_for_video(names_files, start_i=start_i, end_i=end_i, flag_info=flag_info, name=name, cut=cut,
                                 names=names)
    create_mp4(dates=datas, name=name_file, flag_info=flag_info)


def viewing_pictures(names, file_number):
    name_path = os.path.join(new_path, names[file_number])
    info, data = file.open_gz(name_path)

    name_path1 = os.path.join(new_path, names[file_number + 1])
    info1, data1 = file.open_gz(name_path1)

    mode = graphics.print_graphics_cv2_arr(data, data1, data.max(),
                                           names=[names[file_number][:-8], names[file_number + 1][:-8]])
    print(names)
    while True:
        if mode == 0:
            break
        elif mode == 1:
            file_number -= 1
        elif mode == 2:
            file_number += 1

        name_path = os.path.join(new_path, names[file_number])
        info, data = file.open_gz(name_path)

        name_path1 = os.path.join(new_path, names[file_number + 1])
        info1, data1 = file.open_gz(name_path1)

        data_cut = graphics.cut_img(data)
        data1_cut = graphics.cut_img(data1)

        mode = graphics.print_graphics_cv2_arr(data_cut, data1_cut, data_cut.max(),
                                               names=[names[file_number][:-8], names[file_number + 1][:-8]])


current_directory = os.getcwd()

path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")
# "data.ASI0.2023.10.11.5577"
# name="data.ASI0.2024.01.12.5577", name_file="data.ASI0.2024.01.12.5577"
#path = os.path.join(current_directory, "data", "ASI0", "2024", "01", "12")
new_path = os.path.join(path, "5577")

names = file.get_name_file(new_path)

#viewing_pictures(names, file_number)

#graphics.print_graphics_cv2(combined_image, combined_image.max())
#


#create_video(names, start_i=13, flag_info=True, name_file="data.ASI0.2024.01.12.5577", name="data.ASI0.2024.01.12.5577", cut=True)


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



def hist_3d(names, file_number, end=10, name_g="", xlim3d_min=0, xlim3d_max=10000, ylim3d_min=0, ylim3d_max=2):

    #histogram = plt.hist(data_cut.flatten(), bins='auto')
   # print(histogram)
    #plt.show()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection="3d")
    my_cmap = plt.cm.inferno

    count_files = len(names)-end

    for i in range(file_number, count_files):
        # we create evenly spaced bins between the minimum and maximum of the entire dataframe
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path)
        data_cut = graphics.cut_img(data)

        #non_zero_data_cut = data_cut[data_cut != 0]
        
        histvals, _ = np.histogram(data_cut.flatten(), bins="auto")
        histvals = histvals[1:]

        xbins = np.linspace(data_cut.flatten().min().min(), data_cut.flatten().max().max(), len(histvals)+1)
        # and calculate the center and widths of the bars
        xcenter = np.convolve(xbins, np.ones(2), "valid") / 2
        xwidth = np.diff(xbins)

        # print(xbins)
        # print(xcenter)


        ax.bar(left=xcenter, height=histvals, width=xwidth, zs=(i-file_number)/100, zdir="y", alpha=0.666, linewidth=0.3, color=my_cmap((i-file_number)/(count_files-file_number)))

        print(f"{i-file_number}/{count_files-file_number}")


    ax.set_xlabel("bin")
    ax.set_ylabel("column")
    ax.set_zlabel("value")

    # label every other column number
    ax.set_ylim3d(ylim3d_min, ylim3d_max)
    ax.set_xlim3d(xlim3d_min, xlim3d_max)

    plt.title(name_g)

    for angle in range(0, 180):
        ax.view_init(angle, 130)
        print(f"rotate: {angle}/{180}")
        #plt.draw()
        plt.savefig('result/rotanim_' + str(angle+131) + '.png')
        #plt.pause(.001)

    #plt.show()


#hist_3d(names, file_number, len(names)-20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=0.5)
#hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=1.5)


nn = "rotanim_"
name = "rrr0"
# Размеры кадра и частота кадров в видео
date1 = plt.imread(f'result/rotanim_{0}.png')
frame_width = date1.shape[1]
frame_height = date1.shape[0]
fps = 5
# Создаем объект VideoWriter для записи видео в формате MP4
fourcc1 = cv2.VideoWriter_fourcc(*'mp4v')
out1 = cv2.VideoWriter(name + ".mp4", fourcc1, fps, (frame_width, frame_height))

count = 0
for i in range(1, 223):
    frame = cv2.imread(f'result/rotanim_{i}.png')
    out1.write(frame)
    if True:
        count += 1
        print(f"create video: {count}/221")

# Закрываем объект VideoWriter
out1.release()


print('hay')
