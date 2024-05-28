import datetime

from src import graphics
from src import file
import os

import cv2
import numpy as np

import matplotlib.pyplot as plt


def get_names(path, _zip=True):
    new_path = os.path.join(path, "5577")

    names = file.get_name_file(new_path, _zip=_zip)
    return new_path, names


def get_dark(names, new_path, check_name="DARK", _zip=True, fit_format=file.FitsInfo):

    if check_name in names[0]:
        name_path = os.path.join(new_path, names[0])
        info, data = file.open_gz(name_path, _zip=_zip)
        buf = np.array([data])
        buf_time = np.array([fit_format(info).get_datetime()])
    else:
        return None

    for name in names[1:]:
        if not check_name in name:
            break

        name_path = os.path.join(new_path, name)
        info, data = file.open_gz(name_path, _zip=_zip)

        buf = np.vstack((buf, [data]))
        buf_time = np.append(buf_time, fit_format(info).get_datetime())

    return buf, buf_time


def get_dark_AVG(names, new_path, dark_name="DARK", _zip=True, fit_format=file.FitsInfo):
    datas, times = get_dark(names, new_path, dark_name, _zip=_zip, fit_format=fit_format)
    data_avg = (np.mean(datas, axis=0))

    # Получаем среднее время в секундах
    average_time_seconds = sum(dt.timestamp() for dt in times) / len(times)

    # Преобразовываем среднее значение времени обратно в формат datetime.datetime
    time_avg = datetime.datetime.fromtimestamp(average_time_seconds)

    return data_avg, time_avg


def subtract_noise_frame(dark1, dark2, time1, time2, data, date_time):

    k1 = (date_time - time1) / (time2-time1)
    k2 = (time2 - date_time) / (time2-time1)

    fix_data = data.copy()
    fix_data = fix_data - (dark1*k2 + dark2*k1)/2

    return fix_data


def create_all_png(frequency="5577", _zip=True):
    current_directory = os.getcwd()

    path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")
    new_path = os.path.join(path, frequency)

    names = file.get_name_file(new_path)

    save_path = os.path.join(path, frequency + "_img")
    for name in names:
        name_path = os.path.join(new_path, name)
        data = file.open_gz(name_path, _zip=_zip)

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
                         percent_to_trim=0.1, names=False, save_folder=None, figsize=(1920 / 100, 1080 / 100),
                         fit_format=file.FitsInfo, dark=False, dark_name="DARK", n=10000, _zip=True, hists=True, remove_single_pixels=False,
                         correct_matrix=None, Rayleigh=False):

    if correct_matrix is not None:
        corr_matrix = graphics.create_correct_matrix(2, 2048, correct_matrix)

    datas = []
    if dark:
        dark1, time1 = get_dark_AVG(names_files, new_path, dark_name=dark_name, _zip=_zip, fit_format=fit_format)
        dark2, time2 = get_dark_AVG(np.flip(names_files), new_path, dark_name=dark_name, _zip=_zip, fit_format=fit_format)

    if end_i is None:
        end_i = len(names_files)

    for i in range(start_i, end_i):
        name_path = os.path.join(new_path, names_files[i])
        info, data = file.open_gz(name_path, _zip=_zip)

        name_path1 = os.path.join(new_path, names_files[i + 1])
        info1, data1 = file.open_gz(name_path1, _zip=_zip)
        if fit_format == file.FitsInfoAndor:
            data = data[0]
            data1 = data1[0]

        if remove_single_pixels:
            data = graphics.remove_single_pixels(data, False, False, False)
            data1 = graphics.remove_single_pixels(data1, False, False, False)


        if dark:
            time = fit_format(info).get_datetime()
            data = subtract_noise_frame(dark1, dark2, time1, time2, data, time)
            data = (data - data.min()) / (data.max() - data.min())
            data = (data * n).astype(int)

            time = fit_format(info).get_datetime()
            data1 = subtract_noise_frame(dark1, dark2, time1, time2, data1, time)
            data1 = (data1 - data1.min()) / (data1.max() - data1.min())
            data1 = (data1 * n).astype(int)

        if correct_matrix is not None:
            data = data * corr_matrix.astype(np.float64)
            data1 = data1 * corr_matrix.astype(np.float64)
            data[data < 0] = np.nan
            data1[data1 < 0] = np.nan

        if Rayleigh:
            info_f = fit_format(info)
            info_f1 = fit_format(info1)
            data = graphics.calculate_frame_Rayleigh(data, info_f, False)
            data1 = graphics.calculate_frame_Rayleigh(data1, info_f1, False)

        if cut:
            data = graphics.cut_img(data, percent_to_trim)
            data1 = graphics.cut_img(data1, percent_to_trim)

        if names:
            info_f = fit_format(info)
            info_f1 = fit_format(info1)
            img = graphics.create_img_for_video(data, data1, name=name,
                                                names=[info_f.get_norm_time(), info_f1.get_norm_time()])
        else:
            img = graphics.create_img_for_video(data, data1, name=name)
        # plt.imshow(img)
        # plt.show()

        if hists:
            if i == start_i:
                diff1 = None
            diff = data - data1
            img_hist = graphics.create_hists(data, data1, diff, diff1, figsize_x=(img.shape[1]+0.5)/100,
                                             figsize_y=img.shape[0]/100,
                                             xmin_data=0, xmax_data=40000, xmin_diff=-10000, xmax_diff=10000,
                                             ymin_data=0, ymax_data=5000, ymin_diff=0, ymax_diff=14000)
            img_hist_BGR = cv2.cvtColor(img_hist, cv2.COLOR_RGB2BGR)
            img = cv2.vconcat([img, img_hist_BGR])
            diff1 = diff

        datas.append(img)

        if save_folder is not None:

            if not os.path.exists(save_folder):
                # Если папки не существует, создаем её
                os.makedirs(save_folder)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=figsize, dpi=100)
            plt.imshow(img)
            plt.savefig(save_folder + f"/{i}.png")
            plt.close()

        if flag_info:
            print(f"create img: {(i - start_i)}/{end_i - start_i - 1}")
    return datas


def create_video(names_files, new_path, start_i=6, end_i=None, name_file="output", flag_info=False, name=None, cut=False,
                 names=False, save_folder="", save_folder_video=None, save_img=False, name_img_folder="img_for_video",
                 name_video_folder="video", dark=False, dark_name="DARK", fit_format=file.FitsInfo, _zip=True, hists=False, remove_single_pixels=False,
                 correct_matrix=None, Rayleigh=False):

    if end_i is None:
        end_i = len(names_files) - 2

    if save_img:
        datas = create_img_for_video(names_files, new_path, start_i=start_i, end_i=end_i, flag_info=flag_info,
                                     name=name, cut=cut, names=names, save_folder=(save_folder + '/' + name_img_folder),
                                     dark=dark, dark_name=dark_name, fit_format=fit_format, _zip=_zip, hists=hists,
                                     remove_single_pixels=remove_single_pixels, correct_matrix=correct_matrix,
                                     Rayleigh=Rayleigh)
    else:
        datas = create_img_for_video(names_files, new_path, start_i=start_i, end_i=end_i, flag_info=flag_info,
                                     name=name, cut=cut, names=names, dark=dark, dark_name=dark_name, fit_format=fit_format, _zip=_zip,
                                     hists=hists, remove_single_pixels=remove_single_pixels,
                                     correct_matrix=correct_matrix, Rayleigh=Rayleigh)

    if save_folder_video is None:
        save_folder_video = save_folder + "/" + name_video_folder
    create_mp4(dates=datas, name=name_file, flag_info=flag_info, save_folder=save_folder_video)




def viewing_pictures(names, file_number, new_path, dark=True, n = 120000, _zip=True):

    if dark:
        dark1, time1 = get_dark_AVG(names, new_path)
        dark2, time2 = get_dark_AVG(np.flip(names), new_path)

    name_path = os.path.join(new_path, names[file_number])
    info, data = file.open_gz(name_path, _zip=_zip)

    name_path1 = os.path.join(new_path, names[file_number + 1])
    info1, data1 = file.open_gz(name_path1, _zip=_zip)

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
        info, data = file.open_gz(name_path, _zip=_zip)


        if dark:
            time = file.FitsInfo(info).get_datetime()
            data = subtract_noise_frame(dark1, dark2, time1, time2, data, time)
            data = (data - data.min()) / (data.max() - data.min())
            data = (data * n).astype(int)

        name_path1 = os.path.join(new_path, names[file_number + 1])
        info1, data1 = file.open_gz(name_path1, _zip=_zip)

        if dark:
            time = file.FitsInfo(info).get_datetime()
            data1 = subtract_noise_frame(dark1, dark2, time1, time2, data1, time).astype(int)
            data1 = (data1 - data1.min()) / (data1.max() - data1.min())
            data1 = (data1 * n).astype(int)


        data_cut = graphics.cut_img(data, nan=False)
        data1_cut = graphics.cut_img(data1, nan=False)

        mode = graphics.print_graphics_cv2_arr(data_cut, data1_cut, data_cut.max(),
                                               names=[names[file_number][:-8], names[file_number + 1][:-8]])


def create_heatmap(names, new_path, edges=0, start_file=0, end_file=None, log_info=False, title=None, bins=100,
                   auto_contrast=True, cmap="viridis", save_folder=None, limit=None, fit_format=file.FitsInfo, _zip=True):


    if end_file is None:
        end_file = len(names)

    if log_info:
        print('start create heatmap')
    count_files = end_file - start_file - edges * 2
    data_for_heatmap = [0] * count_files
    info_for_heatmap = [0] * count_files
    count = 0



    if auto_contrast:
        name_path = os.path.join(new_path, names[start_file + edges])
        info, data = file.open_gz(name_path, _zip=_zip)
        data_cut = graphics.cut_img(data)
        info_for_heatmap[count] = fit_format(info).get_norm_time()

        print(f"max: {np.max(data_cut[~np.isnan(data_cut)])}")

        _, p2, p98 = graphics.auto_contrast_skimage(data_cut)
        p2 -= 2000-500
        p98 += 1000

        data_c, _, _ = graphics.auto_contrast_skimage(data_cut, p2, p98)

        max_value = np.max(data_c[~np.isnan(data_c)])

        if type(bins) == int:
            print("ggg")
            bins = np.linspace(0, max_value, bins+1)

        data_for_heatmap[count] = graphics.get_bins_hist(data_c, bins=bins)
        #bins = graphics.get_binss_hist(data_c, bins=bins)
        count += 1
        if log_info:
            print(f"create 0/{count_files}, {p2}, {p98}")
            print(f"max: {data_c.max()}")
            print(graphics.get_bins_hist(data_c, bins=bins))
            print(graphics.get_binss_hist(data_c, bins=bins))
            print('\n')
            print(bins)
        start_file += 1

    for i in range(start_file + edges, end_file - edges):
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path, _zip=_zip)
        data_cut = graphics.cut_img(data)
        info_for_heatmap[count] = fit_format(info).get_norm_time()
        if auto_contrast:
            data_c, _, _ = graphics.auto_contrast_skimage(data_cut, p2, p98)
        else:
            data_c = data_cut.copy()
            if not limit is None:
                data_c[data_c > limit] = limit
        data_for_heatmap[count] = graphics.get_bins_hist(data_c, bins=bins)
        count += 1
        if log_info:
            print(f"create {count}/{count_files}")
            # if 45 <= count <= 55:
            #     print(f"max: {data_c.max()}")
            #     print(graphics.get_bins_hist(data_c, bins=bins))
            #     print(graphics.get_binss_hist(data_c, bins=bins))
            #print(graphics.get_binss_hist(data_c, bins=bins))
    data_for_heatmap = np.array(data_for_heatmap)
    transposed_data = np.transpose(data_for_heatmap)

    if not title is None:
        plt.title(title)

    plt.imshow(transposed_data, cmap=cmap)
    colorbar = plt.colorbar()
    colorbar.set_label('n in bin')
    if type(bins) != int:
        plt.ylabel(f"bins ({bins.max()})")
    else:
        plt.ylabel(f"bins")

    plt.xlabel("time")
    plt.xticks(np.arange(0, len(info_for_heatmap), 10), info_for_heatmap[::10], rotation=45, ha='right', fontsize=8)

    if save_folder is None:
        plt.savefig(f'{title}.png')
    else:
        plt.savefig(save_folder + f'/{title}.png')
    # plt.show()
    if log_info:
        print(f"create heatmap: {title}")
