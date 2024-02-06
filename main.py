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

    # Создаем объект VideoWriter для записи видео в формате MP4
    out = cv2.VideoWriter(name+".mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    count = 0
    for i in dates:
        out.write(i)
        if flag_info:
            count += 1
            print(f"create video: {count}/{len(dates)}")

    # Закрываем объект VideoWriter
    out.release()


def create_img_for_video(names, start_i, end_i, flag_info=False, name=None):
    datas = []
    for i in range(start_i, end_i):
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path)

        name_path1 = os.path.join(new_path, names[i + 1])
        info1, data1 = file.open_gz(name_path1)
        img = graphics.create_img_for_video(data, data1, name=name)
        # plt.imshow(img)
        # plt.show()
        datas.append(img)
        if flag_info:
            print(f"create img: {(i-start_i)}/{end_i-start_i-1}")
    return datas


def create_video(names, start_i=6, end_i=None, name_file="output", flag_info=False, name=None):
    if end_i is None:
        end_i = len(names)-2
    datas = create_img_for_video(names, start_i=start_i, end_i=end_i, flag_info=flag_info, name=name)
    create_mp4(dates=datas, name=name_file, flag_info=flag_info)


current_directory = os.getcwd()

#path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")
#"data.ASI0.2023.10.11.5577"
# name="data.ASI0.2024.01.12.5577", name_file="data.ASI0.2024.01.12.5577"
path = os.path.join(current_directory, "data", "ASI0", "2024", "01", "12")
new_path = os.path.join(path, "5577")


names = file.get_name_file(new_path)

name_path = os.path.join(new_path, names[file_number])
info, data = file.open_gz(name_path)


name_path1 = os.path.join(new_path, names[file_number+1])
info1, data1 = file.open_gz(name_path1)


#graphics.print_graphics_cv2(combined_image, combined_image.max())
#
mode = graphics.print_graphics_cv2_arr(data, data1, data.max(), names=[names[file_number][:-8], names[file_number+1][:-8]])
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

    name_path1 = os.path.join(new_path, names[file_number+1])
    info1, data1 = file.open_gz(name_path1)
    mode = graphics.print_graphics_cv2_arr(data, data1, data.max(), names=[names[file_number][:-8], names[file_number+1][:-8]])





#create_video(names, start_i=12, flag_info=True)


print('hay')
