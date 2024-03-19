from src import graphics
from src import file
import os

import cv2
import numpy as np

import matplotlib.pyplot as plt


def get_names(path):
    new_path = os.path.join(path, "5577")

    names = file.get_name_file(new_path)
    return new_path, names


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


def create_mp4(dates, name="output", flag_info=False, save_folder=""):
    # Размеры кадра и частота кадров в видео
    date = dates[0]
    frame_width = date.shape[1]
    frame_height = date.shape[0]
    fps = 1

    if len(save_folder) > 0 and not os.path.exists(save_folder):
        # Если папки не существует, создаем её
        os.makedirs(save_folder)

    # Создаем объект VideoWriter для записи видео в формате MP4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f"{save_folder}/{name}.mp4", fourcc, fps, (frame_width, frame_height))
    count = 0
    for i in dates:
        # plt.imshow(i)
        # plt.show()
        out.write(i)
        if flag_info:
            count += 1
            print(f"create video: {count}/{len(dates)}")

    # Закрываем объект VideoWriter
    out.release()


def create_img_for_video(names_files, new_path, start_i=0, end_i=None, flag_info=False, name=None, cut=False,
                         percent_to_trim=0.1, names=False, save_folder=None, figsize=(1920 / 100, 1080 / 100)):
    datas = []

    if end_i is None:
        end_i = len(names_files)

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

        if not save_folder is None:

            if not os.path.exists(save_folder):
                # Если папки не существует, создаем её
                os.makedirs(save_folder)

            plt.figure(figsize=figsize, dpi=100)
            plt.imshow(img)
            plt.savefig(save_folder + f"/{i}.png")
            plt.close()

        if flag_info:
            print(f"create img: {(i - start_i)}/{end_i - start_i - 1}")
    return datas


def create_video(names_files, start_i=6, end_i=None, name_file="output", flag_info=False, name=None, cut=False,
                 names=False, save_folder="", save_folder_vide=None, save_img=False, name_img_folder="img_for_video",
                 name_video_folder="video"):
    if end_i is None:
        end_i = len(names_files) - 2

    if save_img:
        datas = create_img_for_video(names_files, start_i=start_i, end_i=end_i, flag_info=flag_info, name=name, cut=cut,
                                     names=names, save_folder=(save_folder + '/' + name_img_folder))
    else:
        datas = create_img_for_video(names_files, start_i=start_i, end_i=end_i, flag_info=flag_info, name=name, cut=cut,
                                     names=names)

    if save_folder_vide is None:
        save_folder_vide = save_folder + "/" + name_video_folder
    create_mp4(dates=datas, name=name_file, flag_info=flag_info, save_folder=save_folder_vide)


def viewing_pictures(names, file_number, new_path):
    name_path = os.path.join(new_path, names[file_number])
    info, data = file.open_gz(name_path)

    name_path1 = os.path.join(new_path, names[file_number + 1])
    info1, data1 = file.open_gz(name_path1)

    mode = graphics.print_graphics_cv2_arr(data, data1, data.max(),
                                           names=[names[file_number][:-8], names[file_number + 1][:-8]])

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


def create_heatmap(names, new_path, edges=0, start_file=0, end_file=None, log_info=False, title=None, bins=100,
                   auto_contrast=True, cmap="viridis", save_folder="", limit=None):
    if end_file is None:
        end_file = len(names)

    if log_info:
        print('start create heatmap')
    count_files = end_file - start_file - edges * 2
    data_for_heatmap = [0] * count_files
    info_for_heatmap = [0] * count_files
    count = 0
    for i in range(start_file + edges, end_file - edges):
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path)
        data_cut = graphics.cut_img(data)
        info_for_heatmap[count] = file.FitsInfo(info).get_norm_time()
        if auto_contrast:
            data_c = graphics.auto_contrast_skimage(data_cut)
            data_for_heatmap[count] = graphics.get_bins_hist(data_c, bins=bins)
        else:
            data_c = data_cut.copy()
            if not limit is None:
                data_c[data_c > limit] = limit
            data_for_heatmap[count] = graphics.get_bins_hist(data_c, bins=bins)
        count += 1
        if log_info:
            print(f"create {count}/{count_files}")
    data_for_heatmap = np.array(data_for_heatmap)
    transposed_data = np.transpose(data_for_heatmap)

    if not title is None:
        plt.title(title)

    plt.imshow(transposed_data, cmap=cmap)
    colorbar = plt.colorbar()
    colorbar.set_label('Intensity')
    plt.ylabel("bins")
    plt.xlabel("time")
    plt.xticks(np.arange(0, len(info_for_heatmap), 10), info_for_heatmap[::10], rotation=45, ha='right', fontsize=8)

    plt.savefig(save_folder + f'/{title}.png')
    # plt.show()
    if log_info:
        print(f"create heatmap: {title}")
