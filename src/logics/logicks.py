import datetime
import io
import time

from src import graphics
from src import file
from src import clustering
from src.graphics.graphics import drive_to_color_palette, auto_contrast_skimage
from src.logging import base_log
import os

import cv2
import numpy as np

import matplotlib.pyplot as plt
import pickle


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


def create_mp4(dates, name="output", flag_info=False, save_folder="", fps=1, frames_s=1, logfun=None):
    # Размеры кадра и частота кадров в видео
    date = dates[0]
    frame_width = date.shape[1]
    frame_height = date.shape[0]

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
        for j in range(frames_s):
            out.write(i)

        count += 1
        if flag_info:
            print(f"create video: {count}/{len(dates)}")
        if not logfun is None:
            logfun("create video", count, len(dates))

    # Закрываем объект VideoWriter
    out.release()


def get_equal_intervals_integers(a, b, n):
    if n < 2:
        return [a] if n == 1 else []

    step = (b - a) // (n - 1)
    return [a + step * i for i in range(n)]


def get_hist_p(names_files, new_path, start_i=0, end_i=None, _zip=False, counts_checks=4, bins=2000, cut=False,
               percent_to_trim=0.1, fit_format=file.FitsInfo, dark=False, dark_name="DARK",
               n=10000, corr_matrix=None, Rayleigh=False, flag_info=False, check_frame=None, data_index=None,
               remove_single_pixels=False, multiplication_on_correct_matrix=True):
    if end_i is None:
        end_i = len(names_files)-1

    buf_min_x = []
    buf_max_x = []
    buf_min_y = []
    buf_max_y = []
    buf_min_d = []
    buf_max_d = []
    buf_max_dy = []

    count_frame = end_i - start_i

    if check_frame is None:
        check_frame = []
    elif isinstance(check_frame, int):
        check_frame = [check_frame]
    if count_frame > counts_checks and counts_checks > 0:
        check_frame_buf = set(check_frame).union(get_equal_intervals_integers(start_i, end_i-1, counts_checks))
        check_frame = list(check_frame_buf)
    elif len(check_frame) == 0:
        check_frame = range(start_i, end_i)

    if flag_info:
        print(f"check_frame: {check_frame}")

    for i in check_frame:
        name_path = os.path.join(new_path, names_files[i])
        info, data = file.open_gz(name_path, _zip=_zip)

        name_path1 = os.path.join(new_path, names_files[i + 1])
        info1, data1 = file.open_gz(name_path1, _zip=_zip)

        if not data_index is None:
            data = data[data_index]
            data1 = data1[data_index]

        if remove_single_pixels:
            data = graphics.remove_single_pixels(data, False, False, False)
            data1 = graphics.remove_single_pixels(data1, False, False, False)

        if dark:
            dark1, time1 = get_dark_AVG(names_files, new_path, dark_name=dark_name, _zip=_zip, fit_format=fit_format)
            dark2, time2 = get_dark_AVG(np.flip(names_files), new_path, dark_name=dark_name, _zip=_zip,
                                        fit_format=fit_format)

        if dark:
            time = fit_format(info).get_datetime()
            data = subtract_noise_frame(dark1, dark2, time1, time2, data, time)
            data = (data - data.min()) / (data.max() - data.min())

            time = fit_format(info).get_datetime()
            data1 = subtract_noise_frame(dark1, dark2, time1, time2, data1, time)
            data1 = (data1 - data1.min()) / (data1.max() - data1.min())

        if corr_matrix is not None:
            if multiplication_on_correct_matrix:
                data = data * corr_matrix.astype(np.float64)
                data1 = data1 * corr_matrix.astype(np.float64)
            else:
                data = data / corr_matrix.astype(np.float64)
                data1 = data1 / corr_matrix.astype(np.float64)

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


        # data = (data * n).astype(int)
        # data1 = (data1 * n).astype(int)


        diff = data - data1

        min_x, max_x, min_y, max_y, min_d, max_d, max_dy = graphics.get_hist_p(data, data1, diff, bins)
        if flag_info:
            print('g', min_x, max_x, min_y, max_y, min_d, max_d, max_dy)
        buf_min_x.append(min_x)
        buf_max_x.append(max_x)
        buf_min_y.append(min_y)
        buf_max_y.append(max_y)
        buf_min_d.append(min_d)
        buf_max_d.append(max_d)
        buf_max_dy.append(max_dy)

    return (min(buf_min_x), max(buf_max_x),
            min(buf_min_y), max(buf_max_y),
            min(buf_min_d), max(buf_max_d), max(buf_max_dy))

def create_image(
        names_files=[], new_path="", number=1, flag_info=False, name=None, cut=False,
        percent_to_trim=0.1, save_folder=None, figsize=(1920 / 100, 1080 / 100),
        fit_format=file.FitsInfo, dark=False, dark_name="DARK", n=10000, _zip=True, remove_single_pixels=False,
        correct_matrix=None, Rayleigh=False, logfun=None,
        data_index=None, result_matrix_safe_folder=None, file_name=None, multiplication_on_correct_matrix=True,
        auto_contrast=True, auto_contrast_percentiles=[2, 98]
):
    plt.rcParams.update({"font.size": 14})
    if names_files is None or len(names_files) == 0:
        names_files = file.get_name_file(new_path)

    if correct_matrix is not None:
        corr_matrix = graphics.create_correct_matrix(2, 2048, correct_matrix)
    else:
        corr_matrix = None


    if dark:
        dark1, time1 = get_dark_AVG(names_files, new_path, dark_name=dark_name, _zip=_zip, fit_format=fit_format)
        dark2, time2 = get_dark_AVG(np.flip(names_files), new_path, dark_name=dark_name, _zip=_zip,
                                    fit_format=fit_format)



    name_path = os.path.join(new_path, names_files[number])
    info, data = file.open_gz(name_path, _zip=_zip)

    if not data_index is None:
        data = data[data_index]

    if remove_single_pixels:
        data = graphics.remove_single_pixels(data, False, False, False)

    if dark:
        time = fit_format(info).get_datetime()
        data = subtract_noise_frame(dark1, dark2, time1, time2, data, time)
        data = (data - data.min()) / (data.max() - data.min())

        visual_data = (data * n).astype(int)

    if correct_matrix is not None:
        if multiplication_on_correct_matrix:
            data = data * corr_matrix.astype(np.float64)
        else:
            data = data / corr_matrix.astype(np.float64)

        data[data < 0] = np.nan

    if Rayleigh:
        info_f = fit_format(info)
        data = graphics.calculate_frame_Rayleigh(data, info_f, False)

    if cut:
        data = graphics.cut_img(data, percent_to_trim)

    # plt.imshow(img)
    # plt.show()

    if not result_matrix_safe_folder is None:
        if result_matrix_safe_folder == "" and not save_folder is None and save_folder != "":
            result_matrix_safe_folder = os.path.join(save_folder, "result_matrix")

        if not os.path.exists(result_matrix_safe_folder):
            # Если папки не существует, создаем её
            os.makedirs(result_matrix_safe_folder)

        result_matrix_safe_folder_data = os.path.join(result_matrix_safe_folder, f"{names_files[number]}.pkl")
        with open(result_matrix_safe_folder_data, 'wb') as f:
            pickle.dump(data, f)


    if save_folder is not None:

        if not os.path.exists(save_folder):
            # Если папки не существует, создаем её
            os.makedirs(save_folder)

        if auto_contrast:
            processed_image, _, _ = auto_contrast_skimage(data, q=auto_contrast_percentiles)
        else:
            processed_image = data

        plt.title(f"{name}")

        plt.figure(figsize=figsize, dpi=100)
        plt.imshow(processed_image, cmap="gray")
        plt.axis('off')
        if file_name is None:
            file_name_buf = names_files[number]
        else:
            file_name_buf = file_name
        plt.savefig(save_folder + f"/{file_name_buf}.png", bbox_inches='tight')
        plt.close()

    if flag_info:
        print(f"create img: {number}")

    if logfun:
        logfun("create img", number, "")




def create_img_for_video(names_files=[], new_path="", start_i=0, end_i=None, flag_info=False, name=None, cut=False,
                         percent_to_trim=0.1, names=False, save_folder=None, figsize=(1920 / 100, 1080 / 100),
                         fit_format=file.FitsInfo, dark=False, dark_name="DARK", n=10000, _zip=True, hists=True, remove_single_pixels=False,
                         correct_matrix=None, Rayleigh=False, bins=5000, counts_checks=4, check_frame=None, logfun=None,
                         data_index=None, result_matrix_safe_folder=None, type_diff=1, file_name=None, multiplication_on_correct_matrix=True,
                         upper_limit=500., lower_limit=None, auto_contrast=True, auto_contrast_percentiles=[2, 98]):

    plt.rcParams.update({"font.size": 14})
    if names_files is None or len(names_files)==0:
        names_files = file.get_name_file(new_path)

    if correct_matrix is not None:
        corr_matrix = graphics.create_correct_matrix(2, 2048, correct_matrix)
    else: corr_matrix = None

    datas = []
    diff1 = None

    if hists and counts_checks>1:
        (xmin_data, xmax_data,
         ymin_data, ymax_data,
         xmin_diff, xmax_diff, ymax_diff) = get_hist_p(
                                                        names_files, new_path,
                                                        start_i=start_i, end_i=end_i,
                                                        _zip=_zip, counts_checks=counts_checks, bins=bins,
                                                        cut=cut, percent_to_trim=percent_to_trim,
                                                        fit_format=fit_format,
                                                        dark=dark, dark_name=dark_name,
                                                        corr_matrix=corr_matrix, Rayleigh=Rayleigh,
                                                        flag_info=flag_info, check_frame=check_frame,
                                                        data_index=data_index,
                                                        remove_single_pixels=remove_single_pixels,
                                                        multiplication_on_correct_matrix=multiplication_on_correct_matrix
                                                    )
    elif hists:
        (xmin_data, xmax_data,
         ymin_data, ymax_data,
         xmin_diff, xmax_diff, ymax_diff) = get_hist_p(
            names_files, new_path,
            start_i=start_i, end_i=start_i+1,
            _zip=_zip, counts_checks=1, bins=bins,
            cut=cut, percent_to_trim=percent_to_trim,
            fit_format=fit_format,
            dark=dark, dark_name=dark_name,
            corr_matrix=corr_matrix, Rayleigh=Rayleigh,
            flag_info=flag_info, check_frame=check_frame,
            data_index=data_index,
            multiplication_on_correct_matrix=multiplication_on_correct_matrix
        )


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
        if not data_index is None:
            data = data[data_index]
            data1 = data1[data_index]

        if remove_single_pixels:
            data = graphics.remove_single_pixels(data, False, False, False)
            data1 = graphics.remove_single_pixels(data1, False, False, False)


        if dark:
            time = fit_format(info).get_datetime()
            data = subtract_noise_frame(dark1, dark2, time1, time2, data, time)
            data = (data - data.min()) / (data.max() - data.min())

            time = fit_format(info).get_datetime()
            data1 = subtract_noise_frame(dark1, dark2, time1, time2, data1, time)
            data1 = (data1 - data1.min()) / (data1.max() - data1.min())

        if correct_matrix is not None:
            if multiplication_on_correct_matrix:
                data = data * corr_matrix.astype(np.float64)
                data1 = data1 * corr_matrix.astype(np.float64)
            else:
                data = data / corr_matrix.astype(np.float64)
                data1 = data1 / corr_matrix.astype(np.float64)

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

        # visual_data = (data * n).astype(int)
        visual_data = data
        # visual_data1 = (data1 * n).astype(int)
        visual_data1 = data1

        if names:
            info_f = fit_format(info)
            info_f1 = fit_format(info1)
            img = graphics.create_img_for_video(data, data1, name=name,
                                                names=[info_f.get_norm_time(), info_f1.get_norm_time()], _type=type_diff,
                                                upper_limit=upper_limit, lower_limit=lower_limit, auto_contrast=auto_contrast,
                                                auto_contrast_percentiles=auto_contrast_percentiles)
        else:
            img = graphics.create_img_for_video(data, data1, name=name, _type=type_diff,
                                                upper_limit=upper_limit, lower_limit=lower_limit, auto_contrast=auto_contrast,
                                                auto_contrast_percentiles=auto_contrast_percentiles)
        # plt.imshow(img)
        # plt.show()


        if hists:
            diff = data - data1
            img_hist = graphics.create_hists(data, data1, diff, diff1, figsize_x=(img.shape[1]+0.5)/100,
                                             figsize_y=img.shape[0]/100,
                                             xmin_data=xmin_data, xmax_data=xmax_data, xmin_diff=xmin_diff, xmax_diff=xmax_diff,
                                             ymin_data=ymin_data, ymax_data=ymax_data, ymin_diff=0, ymax_diff=ymax_diff,
                                             bins=bins)
            img_hist_BGR = cv2.cvtColor(img_hist, cv2.COLOR_RGB2BGR)
            img = cv2.vconcat([img, img_hist_BGR])
            diff1 = diff
        datas.append(img)

        if not result_matrix_safe_folder is None:
            if result_matrix_safe_folder == "" and not save_folder is None and save_folder != "":
                result_matrix_safe_folder = os.path.join(save_folder, "result_matrix")

            if not os.path.exists(result_matrix_safe_folder):
                # Если папки не существует, создаем её
                os.makedirs(result_matrix_safe_folder)

            dir_name = file.remove_extensions(names_files[i])
            result_matrix_safe_folder_frame = os.path.join(result_matrix_safe_folder, f"{dir_name}")
            if not os.path.exists(result_matrix_safe_folder_frame):
                # Если папки не существует, создаем её
                os.makedirs(result_matrix_safe_folder_frame)

            result_matrix_safe_folder_data = os.path.join(result_matrix_safe_folder_frame, f"{names_files[i]}.pkl")
            with open(result_matrix_safe_folder_data, 'wb') as f:
                pickle.dump(data, f)

            result_matrix_safe_folder_data1 = os.path.join(result_matrix_safe_folder_frame, f"{names_files[i + 1]}.pkl")
            with open(result_matrix_safe_folder_data1, 'wb') as f:
                pickle.dump(data1, f)

        if save_folder is not None:

            if not os.path.exists(save_folder):
                # Если папки не существует, создаем её
                os.makedirs(save_folder)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=figsize, dpi=100)
            plt.imshow(img)
            plt.axis('off')
            # plt.savefig(save_folder + f"/{i}.png", bbox_inches='tight')
            if file_name is None:
                file_name_buf = names_files[i]
            else:
                file_name_buf = file_name
            plt.savefig(save_folder + f"/{file_name_buf}.png", bbox_inches='tight')
            plt.close()

        if flag_info:
            print(f"create img: {(i - start_i +1)}/{end_i - start_i}")

        if logfun:
            logfun("create img", i-start_i+1, end_i-start_i)
    return datas


def create_video(names_files=[], new_path="", start_i=6, end_i=None, name_file="output", flag_info=False, name=None, cut=False,
                 names=False, save_folder="", save_folder_video=None, save_img=False, name_img_folder="img_for_video",
                 name_video_folder="video", dark=False, dark_name="DARK", fit_format=file.FitsInfo, _zip=True, hists=False, remove_single_pixels=False,
                 correct_matrix=None, Rayleigh=False, logfun=None, counts_checks=4, check_frame=None, bins=5000, fps=1, frames_s=1, data_index=None,
                 result_matrix_safe_folder=None, type_diff=1, multiplication_on_correct_matrix=True, upper_limit=500., lower_limit=None,
                 auto_contrast=True, auto_contrast_percentiles=[2, 98]):

    if not result_matrix_safe_folder is None and result_matrix_safe_folder != "":
        result_matrix_safe_folder = os.path.join(save_folder, result_matrix_safe_folder)

    if result_matrix_safe_folder == "" and not save_folder is None and not save_folder == "":
        result_matrix_safe_folder = os.path.join(save_folder, "result_matrix")

    if end_i is None:
        end_i = len(names_files) - 2

    if save_img:
        datas = create_img_for_video(names_files, new_path, start_i=start_i, end_i=end_i, flag_info=flag_info,
                                     name=name, cut=cut, names=names, save_folder=(save_folder + '/' + name_img_folder),
                                     dark=dark, dark_name=dark_name, fit_format=fit_format, _zip=_zip, hists=hists,
                                     remove_single_pixels=remove_single_pixels, correct_matrix=correct_matrix,
                                     Rayleigh=Rayleigh, logfun=logfun, counts_checks=counts_checks, bins=bins, check_frame=check_frame,
                                     data_index=data_index, result_matrix_safe_folder=result_matrix_safe_folder,
                                     type_diff=type_diff, multiplication_on_correct_matrix=multiplication_on_correct_matrix,
                                     upper_limit=upper_limit, lower_limit=lower_limit, auto_contrast=auto_contrast,
                                     auto_contrast_percentiles=auto_contrast_percentiles)
    else:
        datas = create_img_for_video(names_files, new_path, start_i=start_i, end_i=end_i, flag_info=flag_info,
                                     name=name, cut=cut, names=names, dark=dark, dark_name=dark_name, fit_format=fit_format, _zip=_zip,
                                     hists=hists, remove_single_pixels=remove_single_pixels,
                                     correct_matrix=correct_matrix, Rayleigh=Rayleigh, logfun=logfun, counts_checks=counts_checks, bins=bins,
                                     check_frame=check_frame, data_index=data_index, result_matrix_safe_folder=result_matrix_safe_folder,
                                     type_diff=type_diff, multiplication_on_correct_matrix=multiplication_on_correct_matrix,
                                     upper_limit=upper_limit, lower_limit=lower_limit, auto_contrast=auto_contrast,
                                     auto_contrast_percentiles=auto_contrast_percentiles)

    if save_folder_video is None:
        save_folder_video = save_folder + "/" + name_video_folder
    create_mp4(dates=datas, name=name_file, flag_info=flag_info, save_folder=save_folder_video, fps=fps, frames_s=frames_s, logfun=logfun)

    return f"Video create: {save_folder}"



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


def create_heatmap(names=None, new_path=r"", edges=0, start_file=0, end_file=None, log_info=False, title=None, bins=100,
                   auto_contrast=True, cmap="viridis", save_folder=None, fit_format=file.FitsInfo, _zip=True,
                   counts_checks=4, check_frame=None, remove_single_pixels=False, correct_matrix=None, Rayleigh=False,
                   dark=False, dark_name="DARK", cut=False, percent_to_trim=0.1, data_index=None, flag_info=None,
                   multiplication_on_correct_matrix=True, q=[2, 50], name_file=None, result_auto_contrast=True):

    if names is None or len(names)==0:
        names = file.get_name_file(new_path)

    if end_file is None:
        end_file = len(names)

    if correct_matrix is not None:
        corr_matrix = graphics.create_correct_matrix(2, 2048, correct_matrix)
    else:
        corr_matrix = None

    if dark:
        dark1, time1 = get_dark_AVG(names, new_path, dark_name=dark_name, _zip=_zip, fit_format=fit_format)
        dark2, time2 = get_dark_AVG(np.flip(names), new_path, dark_name=dark_name, _zip=_zip, fit_format=fit_format)

    (xmin_data, xmax_data,
     ymin_data, ymax_data,
     _, _, _) = get_hist_p(
        names, new_path,
        start_i=start_file, end_i=end_file,
        _zip=_zip, counts_checks=counts_checks, bins=bins,
        cut=cut, percent_to_trim=percent_to_trim,
        fit_format=fit_format,
        dark=dark, dark_name=dark_name,
        corr_matrix=corr_matrix, Rayleigh=Rayleigh,
        flag_info=flag_info, check_frame=check_frame,
        data_index=data_index,
        remove_single_pixels=remove_single_pixels,
        multiplication_on_correct_matrix=multiplication_on_correct_matrix
    )


    data_for_heatmap = []
    info_for_heatmap = []


    for frame in range(start_file+edges, end_file-edges):
        name_path = os.path.join(new_path, names[frame])
        info, data = file.open_gz(name_path, _zip=_zip)

        if not data_index is None:
            data = data[data_index]

        if remove_single_pixels:
            data = graphics.remove_single_pixels(data, False, False, False)

        if dark:
            time = fit_format(info).get_datetime()
            data = subtract_noise_frame(dark1, dark2, time1, time2, data, time)
            data = (data - data.min()) / (data.max() - data.min())

        if correct_matrix is not None:
            if multiplication_on_correct_matrix:
                data = data * corr_matrix.astype(np.float64)
            else:
                data = data / corr_matrix.astype(np.float64)

            data[data < 0] = np.nan

        if Rayleigh:
            info_f = fit_format(info)
            data = graphics.calculate_frame_Rayleigh(data, info_f, False)

        if cut:
            data = graphics.cut_img(data, percent_to_trim)

        if auto_contrast:
            data, _, _ = graphics.auto_contrast_skimage(data, q=q)

        result_hist = graphics.create_hists(data, data, data,
                                                     xmin_data=xmin_data, xmax_data=xmax_data,
                                                     ymin_data=ymin_data, ymax_data=ymax_data, ymin_diff=0, bins=bins,
                                                     return_data=True)
        result_hist, _, _ = result_hist
        data_for_heatmap.append(result_hist)
        info_for_heatmap.append(fit_format(info).get_datetime().time())

    data_for_heatmap = np.array(data_for_heatmap)
    transposed_data = np.transpose(data_for_heatmap)
    # transposed_data = data_for_heatmap

    if not title is None:
        plt.title(title)

    if result_auto_contrast:
        transposed_data, _, _ = graphics.auto_contrast_skimage(transposed_data)

    plt.imshow(transposed_data, cmap=cmap, aspect='auto')
    colorbar = plt.colorbar()
    colorbar.set_label('n in bin')
    # if type(bins) != int:
    #     plt.ylabel(f"bins ({bins.max()})")
    # else:
    #     plt.ylabel(f"bins")


    y_positions = np.linspace(0, transposed_data.shape[0] - 1, 10)  # Позиции меток на графике
    y_labels = np.linspace(ymin_data, ymax_data, 10)  # Значения меток от 0 до 1243

    plt.yticks(y_positions, [int(label) for label in y_labels], fontsize=8)  # Устанавливаем метки
    plt.ylabel("y")

    plt.xlabel("time")
    plt.xticks(np.arange(0, len(info_for_heatmap), 10), info_for_heatmap[::10], rotation=45, ha='right', fontsize=8)

    if name_file is None:
        name_file = title

    if save_folder is not None:

        if not os.path.exists(save_folder):
            # Если папки не существует, создаем её
            os.makedirs(save_folder)

    if save_folder is None:
        plt.savefig(f'{name_file}.png')
    else:
        plt.savefig(save_folder + f'/{name_file}.png')
    # plt.show()
    if log_info:
        print(f"create heatmap: {title}")
    plt.close()



def create_heatmap1(names=None, new_path=r"", edges=0, start_file=0, end_file=None, log_info=False, title=None, bins=100,
                   auto_contrast=True, cmap="viridis", save_folder=None, limit=None, fit_format=file.FitsInfo, _zip=True):

    if names is None or len(names)==0:
        names = file.get_name_file(new_path)

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
        # p2 -= 2000-500
        # p98 += 1000

        data_c, _, _ = graphics.auto_contrast_skimage(data_cut, p2, p98)

        max_value = np.max(data_c[~np.isnan(data_c)])

        if type(bins) == int:
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


def save_heat_map(names, new_path, save_folder, type_fits:file.FitsInfo=file.FitsInfo2014, _zip=False,
                  start_i=0, end_i=None ,name_operation="Create diff", log_fun=base_log, logs=False,
                  use_names=True):

    if end_i is None:
        end_i = len(names)-1

    if logs:
        log_fun("Start", "save_heat_map", f"start_i={start_i}/end_i={end_i}")

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        if logs:
            log_fun("Create dir", save_folder, f"{new_path}")

    for i in range(start_i, end_i):
        data, data1, diff, info, info1 = clustering.work_with_date(names, new_path, i, percent_to_trim=0.1,
                                                        _zip=_zip, type_fits=type_fits)


        diff = data.astype(float) - data1.astype(float)
        if logs:
            log_fun(name_operation, i, end_i)

        if use_names:
            name_file = names[i+1]
        else :
            name_file = i
        graphics.save_heat_map(diff, save_folder=save_folder, nameFile=name_file, color_bar=False)

    if logs:
        log_fun("End", "save_heat_map", "")






def write_data_in_file(names, new_path, save_folder, start_i=0, end_i=None,
                       image_folder=None, with_time=False, name_file='slic_dbscan_RGB',
                       time_measurement=False, log_fun=base_log,
                       save_folder_clusters=None, logs=False, type_fits=file.FitsInfo2014,
                       _zip=False, save_folder_slic=None, eps=1.2, bin_result=False, min_clustering_area=0,
                       use_names=True):
    if logs:
        log_fun("Start", "write_data_in_file", f"{new_path}")

    if end_i is None:
        end_i = len(names)-1

    if time_measurement:
        start_time = time.time()

    for i in range(start_i, end_i):
        if not image_folder is None:
            if use_names:
                image_file = os.path.join(image_folder, f"{names[i+1]}.png")
            else:
                image_file = os.path.join(image_folder, f"{i}.png")
        else:
            image_file = None

        if use_names:
            name_img = f"{names[i]}"
        else:
            name_img = f"{i}"
        if with_time:
            buf, labels, img, info, info1 = clustering.SLIC_DBSCAN(names_files=names, new_path=new_path, i=i,
                                                                   return_img=True, all_info=False,
                                                                   save_folder=save_folder+"\\"+name_file,
                                                                   nameFile=f"{i}", image_file=image_file,
                                                                   suptitle=name_img,
                                                                   save_folder_clusters=save_folder_clusters,
                                                                   log_fun=log_fun, logs=logs, type_fits=type_fits,
                                                                   _zip=_zip, save_folder_slic=save_folder_slic,
                                                                   eps=eps, bin_result=bin_result,
                                                                   min_clustering_area=min_clustering_area)
        else:
            buf, labels, img = clustering.SLIC_DBSCAN(names_files=names, new_path=new_path, i=i, return_img=True,
                                                      all_info=False, save_folder=save_folder+"\\"+name_file,
                                                      nameFile=name_img, image_file=image_file, suptitle=f"Frame {i}",
                                                      save_folder_clusters=save_folder_clusters, log_fun=log_fun,
                                                      logs=logs, type_fits=type_fits, _zip=_zip,
                                                      save_folder_slic=save_folder_slic, eps=eps, bin_result=bin_result,
                                                      min_clustering_area=min_clustering_area)

        # plt.imshow(img)
        # plt.show()
        # print(buf, info.get_norm_time(), info1.get_norm_time())
        if logs:
            log_fun("Create cluster img", i, end_i)

        # Открытие файла в режиме добавления (append)
        with open(f"{save_folder}\\count_{name_file}.txt", "a", encoding="utf-8") as f:
            # Запись дополнительного текста в файл
            if with_time:
                f.write(f"{len(buf)}   {info.get_norm_time()}   {info1.get_norm_time()}   {i}   {i+1}\n")
            else:
                f.write(f"{len(buf)}   {i}   {i+1}\n")


    # Засеките время окончания
    if time_measurement:
        end_time = time.time()
        with open(f"{save_folder}\\count_{name_file}.txt", "a", encoding="utf-8") as file:
            # Запись дополнительного текста в файл
            file.write(f"{end_time-start_time}\n")

    if logs:
        log_fun("End", "write_data_in_file", f"files: {start_i}/{end_i}")