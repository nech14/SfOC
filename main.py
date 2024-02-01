from src import graphics
from src import file
import os

import cv2

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


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

name_path = os.path.join(new_path, names[12])

info, data = file.open_gz(name_path)



name_path1 = os.path.join(new_path, names[11])
info1, data1 = file.open_gz(name_path1)

diff = cv2.absdiff(data, data1)
result = data - data1


#cv2.imshow('result', diff)
#cv2.imshow('i1', data)
#cv2.imshow('i2', data1)q
#cv2.waitKey()
#cv2.destroyAllWindows()

#graphics.print_hist_and_graphics(data)
#graphics.print_graphics(data)


#graphics.print_graphics_cv2(diff, diff.max())


combined_image = cv2.hconcat([data, data1, diff])

#graphics.print_graphics_cv2(combined_image, combined_image.max())

graphics.print_graphics_cv2_arr(data, data1, data.max())

print('hay')
