from src import graphics
from src import file
import os

import cv2

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


current_directory = os.getcwd()

path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")
new_path = os.path.join(path, "5577")

names = file.get_name_file(new_path)

name_path = os.path.join(new_path, names[file_number])
info, data = file.open_gz(name_path)


name_path1 = os.path.join(new_path, names[file_number+1])
info1, data1 = file.open_gz(name_path1)


#graphics.print_graphics_cv2(combined_image, combined_image.max())

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

print('hay')
