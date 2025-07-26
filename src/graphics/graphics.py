import os

import matplotlib.pyplot as plt
import numpy as np
import cv2
from skimage.measure import label, regionprops
from skimage import exposure
from matplotlib import cm
from matplotlib.colors import Normalize
from PIL import Image
from datetime import datetime
from src import file


def print_graphics(data):
    plt.figure()
    plt.subplot(121)
    plt.imshow(data, origin='lower', cmap='gray')
    plt.subplot(122)
    plt.imshow(data, origin='lower')
    plt.show()


def print_graphics_binary(data):
    buf = data.copy()
    buf[buf > 0] = 1
    labeled = label(buf)

    plt.figure()
    plt.subplot(121)
    plt.imshow(buf, origin='lower', cmap='gray')
    plt.subplot(122)
    plt.imshow(labeled, origin='lower')

    plt.suptitle(f"number of objects: {labeled.max()}", fontsize=16)

    plt.show()


def save_graphics(data, path, name):
    fig = plt.figure(figsize=(20, 10))

    plt.subplot(121)
    plt.imshow(data, origin='lower', cmap='gray')
    plt.subplot(122)
    plt.imshow(data, origin='lower')
    plt.savefig(path + '/' + name + '.png')
    plt.close()


def print_hist_and_graphics(data, vmin=5000, vmax=15000, name=""):
    plt.figure()
    plt.subplot(121)
    non_zero_values = data[data > 0]
    histogram = plt.hist(non_zero_values.flatten(), bins='auto')
    plt.subplot(122)
    plt.imshow(data, cmap='gray', vmin=vmin, vmax=vmax)
    plt.colorbar()

    if len(name) > 0:
        plt.suptitle(name, fontsize=16)

    plt.show()


def drive_to_color_palette(combined_image, dlimit, ulimit, cmap):

    buf_combined_image = np.nan_to_num(combined_image, nan=0)

    cmap_image = np.clip(buf_combined_image, dlimit, ulimit)
    cmap_image = (cmap_image - dlimit) / (ulimit - dlimit)  # Нормализация значений
    cmap_image = (cmap_image * 255).astype(np.uint8)  # Конвертация в формат uint8

    # Применение цветовой карты
    cmap_image = cmap(cmap_image)

    # Преобразование в BGR (OpenCV использует формат BGR)
    cmap_image = (cmap_image[:, :, 0] * 255).astype(np.uint8)
    return cmap_image[:, :]


def drive_to_color_palette_heat_mao(data):
    norm = Normalize(vmin=data.min(), vmax=data.max())

    # Создаем цветовую карту для отображения положительных и отрицательных значений
    cmap_RdBu = cm.get_cmap("RdBu")

    # Применяем цветовую карту к нормализованным значениям
    color_mapped = (cmap_RdBu(norm(data))[:, :, :3] * 255).astype(np.uint8)

    return color_mapped


def print_graphics_cv2(data, max_limit=255, dlimit=0):
    image = data.copy()
    ulimit = max_limit
    dlimit = 0

    def uupdate(value):
        nonlocal ulimit
        ulimit = value

    def dupdate(value):
        nonlocal dlimit
        dlimit = value

    cv2.namedWindow("Graphic", cv2.WINDOW_KEEPRATIO)

    cv2.createTrackbar("U", "Graphic", ulimit, max_limit, uupdate)
    cv2.createTrackbar("D", "Graphic", dlimit, max_limit, dupdate)

    cmap = plt.get_cmap('gray')

    while True:
        cmap_image = drive_to_color_palette(image, dlimit, ulimit, cmap)

        cv2.imshow("Graphic", cmap_image)

        if cv2.waitKey(1) == ord('q'):
            break

        if cv2.waitKey(1) == ord('f'):
            print_hist_and_graphics(image, dlimit, ulimit)


def save_heat_map(data_heat, upper_limit=500., lower_limit=None, save_folder=None, file_name=None, nameFile="diff", color_bar=True):
    if lower_limit is None:
        lower_limit = -upper_limit

    fig, ax = plt.subplots(figsize=(8, 8))
    #fig, ax = plt.subplots(figsize=(1024 / 100, 1424 / 100))
    #print(f"hsdjhfds:{data_heat.shape}")
    mask = np.ma.masked_equal(data_heat, 0)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=lower_limit, vmax=upper_limit)
    if color_bar:
        cbar = plt.colorbar(shrink=0.8, fraction=0.1)
        for text in cbar.ax.get_yticklabels():
            text.set_color('white')
    plt.axis('off')
    fig.set_facecolor('black')



    #plt.savefig(buffer, format="png")
    canvas = plt.gcf().canvas
    #canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    rgb_string = canvas.tostring_rgb()

    image_array = np.frombuffer(rgb_string, dtype=np.uint8)
    image_array = image_array.reshape(canvas.get_width_height()[::-1] + (3,))

    plt.close(fig)

    if color_bar:
        image_array = image_array[144:-144, :]
    else:
        image_array = image_array[80:-80, :]
    #image_array = image_array[137:-138, 114:-54]

    # print(image_array.shape)
    # plt.imshow(image_array)
    # plt.show()

    if not save_folder is None:
        # Преобразование массива numpy в изображение PIL
        image = Image.fromarray(image_array)


        os.makedirs(save_folder, exist_ok=True)
        if file_name is None:
            file_name = f"{nameFile}.png"
        output_path = os.path.join(save_folder, file_name)
        # Сохранение изображения
        image.save(output_path)
        image.close()
        # plt.figure()
        # plt.imshow(image_array)
        # os.makedirs(save_folder, exist_ok=True)
        # if file_name is None:
        #     file_name = f"{nameFile}.png"
        # output_path = os.path.join(save_folder, file_name)
        # plt.savefig(output_path)
        # plt.close()


    return image_array

def print_heat_map(data_heat, data_base=None):
    if not data_base is None:
        r = 2
    else:
        r = 2

    c = 2

    pp = 1000

    plt.subplot(r, c, 1)

    plt.imshow(data_heat, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar()

    plt.subplot(r, c, 2)
    plt.imshow(data_heat, cmap="gray", vmin=-pp, vmax=pp)
    plt.colorbar()

    if not data_base is None:
        h_buf_diff = data_heat.copy()
        h_buf_diff[(h_buf_diff < 1000) & (h_buf_diff > -1000)] = None
        plt.subplot(r, c, 3)
        plt.imshow(h_buf_diff, cmap="RdBu_r", interpolation='nearest')
        plt.colorbar()

        plt.subplot(r, c, 4)
        plt.imshow(data_base, cmap="gray")
        plt.colorbar()
    else:
        plt.subplot(r, 1, 2)
        histogram = plt.hist(data_heat.flatten(), bins='auto')
        plt.xlim(-pp, pp)

    plt.show()


def auto_contrast(data):
    image = data.copy()
    # Автоматическое выравнивание гистограммы
    non_zero_values = image[image > 0]
    q_d = 2
    q_u = 98
    while True:
        p2, p98 = np.percentile(non_zero_values, (q_d, q_u))
        result = exposure.rescale_intensity(image, in_range=(p2, p98))
        print(p2, p98, q_d, q_u)

        clahe = exposure.equalize_adapthist(image, clip_limit=0.03)
        result1 = (clahe * 255).astype('uint8')

        cv2.imshow('Original', result1)
        cv2.imshow('Auto Contrast', result)
        key = cv2.waitKey(0)

        if key == ord("q"):
            break
        elif key == ord('a'):
            q_d -= 1
        elif key == ord('d'):
            q_d += 1
        elif key == ord('w'):
            q_u += 1
        elif key == ord('s'):
            q_u -= 1
    cv2.destroyAllWindows()


def auto_contrast_skimage(data, p2=None, p98=None, auto_contrast_percentiles=[2, 98]):
    image = data.copy()
    non_zero_values = image[image > 0]
    if p2 is None or p98 is None:
        p2, p98 = np.percentile(non_zero_values, (auto_contrast_percentiles[0], auto_contrast_percentiles[1]))
    result = exposure.rescale_intensity(image, in_range=(p2, p98))
    return result, p2, p98


def auto_contrast_cv2(data):
    image = data.copy()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(10, 10))
    result = clahe.apply(image)
    return result


def get_hist_for_video(data):
    non_zero_values = data[data > 0]

    percentiles = np.percentile(non_zero_values, [0, 99.9])
    range = (percentiles[0], percentiles[1])

    histogram = plt.hist(non_zero_values.flatten(), bins="auto")
    #print(range)
    plt.xlim(range[0], range[1])
    plt.show()


def get_hist_diff_for_video(data, pp=1000):
    histogram = plt.hist(data.flatten(), bins='auto')
    plt.xlim(-pp, pp)
    plt.show()


def get_heat_map_diff_for_video(data, pp=1000, cmap="RdBu_r"):
    plt.imshow(data, cmap=cmap, interpolation='nearest', vmin=-pp, vmax=pp)
    plt.colorbar()
    plt.show()


def hist_all(data, data1, diff, diff1=None, bins="auto"):

    plt.subplot(1, 3, 2)
    non_zero_values = data[data > 0]
    non_zero_values1 = data1[data1 > 0]
    histogram = plt.hist(non_zero_values.flatten(), bins=bins)

    histogram1 = plt.hist(non_zero_values1.flatten(), bins=bins, alpha=0.5)
    plt.show()
    pass


def hist_datas(data, data1, mode=0, show=False, diff=False, pp=500, bins="auto"):

    r = 2
    c = 2
    if diff:
        c = 3
        h_diff = data.astype(float) - data1.astype(float)
        plt.subplot(r, c, c)
        plt.imshow(h_diff, cmap="RdBu_r", interpolation='nearest', vmin=-pp, vmax=pp)
        plt.colorbar()
        plt.title("diff")



    plt.subplot(r, c, 1)
    data_c, _, _ = auto_contrast_skimage(data)
    plt.imshow(data_c, cmap='gray')


    plt.subplot(r, c, 2)
    data_c1, _, _ = auto_contrast_skimage(data1)
    plt.imshow(data_c1, cmap='gray')

    plt.subplot(r, 1, 2)
    non_zero_values = data[data > 0]
    non_zero_values1 = data1[data1 > 0]
    histogram = plt.hist(non_zero_values.flatten(), bins=bins)

    histogram1= plt.hist(non_zero_values1.flatten(), bins=bins, alpha=0.5)
    plt.savefig('hist2.png')



def get_bins_hist(data, bins=100):
    non_zero_values = data[data > 0]
    n, bins, _ = plt.hist(non_zero_values.flatten(), bins=bins)
    plt.close()
    return n


def get_binss_hist(data, bins=100):
    non_zero_values = data[data > 0]
    n, bins, _ = plt.hist(non_zero_values.flatten(), bins=bins)
    plt.close()
    return bins


def print_graphics_cv2_arr(data, data1, max_limit=255, dlimit=0, names=None, nameWindow="GraphicData"):
    if names is None:
        names = ['1', '2']

    combined_image = cv2.hconcat([data, data1])

    ulimit = max_limit
    dlimit = 0
    ulimit_diff = max_limit
    dlimit_diff = 0

    result_flag = True

    def uupdate(value):
        nonlocal ulimit
        ulimit = value

    def dupdate(value):
        nonlocal dlimit
        dlimit = value

    def uupdate_diff(value):
        nonlocal ulimit_diff
        ulimit_diff = value

    def dupdate_diff(value):
        nonlocal dlimit_diff
        dlimit_diff = value

    cv2.namedWindow(nameWindow, cv2.WINDOW_KEEPRATIO)

    cv2.createTrackbar("U", nameWindow, ulimit, max_limit, uupdate)
    cv2.createTrackbar("D", nameWindow, dlimit, max_limit, dupdate)

    cv2.namedWindow("GraphicDiff", cv2.WINDOW_KEEPRATIO)
    cv2.createTrackbar("U", "GraphicDiff", ulimit_diff, max_limit, uupdate_diff)
    cv2.createTrackbar("D", "GraphicDiff", dlimit_diff, max_limit, dupdate_diff)

    cmap = plt.get_cmap('gray')

    p_flag = True
    s_flag = False
    while True:

        cmap_image = drive_to_color_palette(combined_image, dlimit, ulimit, cmap)
        if p_flag:
            top_border = 50
            bottom_border = 50
            left_border = 50
            right_border = 50

            # Расширение изображения
            expanded_image = cv2.copyMakeBorder(cmap_image, top_border, bottom_border, left_border, right_border,
                                                cv2.BORDER_CONSTANT)

            # Добавление текста
            text = names[0] + "  |  " + names[1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.4
            font_thickness = 1
            text_color = (255, 255, 255)  # Цвет текста в формате BGR

            # Определение размера текста для вычисления координат центра
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

            # Определение координат текста в расширенной области
            text_position = ((expanded_image.shape[1] - text_size[0]) // 2, cmap_image.shape[0] + top_border + 30)

            # Нанесение текста на изображение
            cv2.putText(expanded_image, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)
            cmap_image = expanded_image

        cv2.imshow(nameWindow, cmap_image)

        key = cv2.waitKey(1)

        if result_flag:
            if not s_flag:
                # cmap_image1 = drive_to_color_palette(data, dlimit, ulimit, cmap)
                cmap_image1 = data.copy()
                cmap_image1[(cmap_image1 < dlimit) | (cmap_image1 > ulimit)] = 0

                # cmap_image2 = drive_to_color_palette(data1, dlimit, ulimit, cmap)
                cmap_image2 = data1.copy()
                cmap_image2[(cmap_image2 < dlimit) | (cmap_image2 > ulimit)] = 0

                diff = cv2.absdiff(cmap_image1, cmap_image2)

            diff_cmap = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)
            # diff_cmap = auto_contrast_cv2(diff)

            cv2.imshow("GraphicDiff", diff_cmap)

            if key == ord('h'):
                # f_diff = diff.copy()
                # f_diff[f_diff < dlimit_diff] = 0.
                # f_diff[f_diff > ulimit_diff] = ulimit_diff
                print_hist_and_graphics(diff, dlimit_diff, ulimit_diff)

            elif key == ord('x'):
                ulimit_diff = 1500
                dlimit_diff = 800
                cv2.setTrackbarPos("U", "GraphicDiff", ulimit_diff)
                cv2.setTrackbarPos("D", "GraphicDiff", dlimit_diff)
            elif key == ord('o'):
                ulimit_diff = max_limit
                dlimit_diff = 0
                cv2.setTrackbarPos("U", "GraphicDiff", ulimit_diff)
                cv2.setTrackbarPos("D", "GraphicDiff", dlimit_diff)
            elif key == ord('b'):
                f_diff = diff.copy()
                f_diff[f_diff < dlimit_diff] = 0
                f_diff[f_diff > ulimit_diff] = ulimit_diff

                print_graphics_binary(np.flip(f_diff, axis=0))
            elif key == ord('s'):
                s_flag = not s_flag
            elif key == ord('n'):
                h_diff = data.astype(float) - data1.astype(float)


                h, b = np.histogram(h_diff, bins=2000)
                print(len(h), h)
                print(len(b), b)

                h_diff[h_diff==0] = None
                print_heat_map(h_diff)
            elif key == ord('m'):
                h_diff = data.astype(float) - data1.astype(float)
                print_heat_map(h_diff, diff)
            elif key == ord('a'):
                h_diff = data.astype(float) - data1.astype(float)
                save_heat_map(h_diff)
                print('ffffffffffffffffffff')
            elif key == ord('i'):
                h_diff = data.astype(float) - data1.astype(float)

                # Нормализуем значения в диапазон [0, 1]
                color_mapped = drive_to_color_palette_heat_mao(h_diff)

                # Отображаем изображение с цветовой картой
                cv2.namedWindow("Color Mapped Image", cv2.WINDOW_KEEPRATIO)
                cv2.imshow('Color Mapped Image', color_mapped)
            elif key == ord('u'):
                h_diff = data.astype(float) - data1.astype(float)

                h_diff[h_diff == 0] = None

                # Нормализуем значения в диапазон [0, 1]
                color_mapped = drive_to_color_palette_heat_mao(h_diff)

                # Отображаем изображение с цветовой картой
                cv2.namedWindow("Color Mapped Image", cv2.WINDOW_KEEPRATIO)
                cv2.imshow('Color Mapped Image', color_mapped)

        if key == ord('q'):
            cv2.destroyAllWindows()
            return 0
        elif key == ord('p'):
            p_flag = not p_flag

        elif key == ord('g'):
            result_flag = not result_flag
            if result_flag:
                cv2.namedWindow("GraphicDiff", cv2.WINDOW_KEEPRATIO)
                ulimit_diff = ulimit
                dlimit_diff = dlimit
                cv2.createTrackbar("U", "GraphicDiff", ulimit_diff, max_limit, uupdate_diff)
                cv2.createTrackbar("D", "GraphicDiff", dlimit_diff, max_limit, dupdate_diff)
            if not result_flag:
                cv2.destroyWindow("GraphicDiff")
        elif key == ord('1'):

            get_hist_for_video(data)

            print_hist_and_graphics(data, dlimit, ulimit, name=names[0])
        elif key == ord('2'):

            h, b = np.histogram(data1, bins="auto")
            print(h, b)

            print_hist_and_graphics(data1, dlimit, ulimit, name=names[1])
        elif key == ord('3'):
            hist_datas(data, data1)
            cmap_image1 = data.copy()
            cmap_image1[(cmap_image1 < dlimit)] = 0
            cmap_image1[(cmap_image1 > ulimit)] = ulimit
            print_hist_and_graphics(cmap_image1, dlimit, ulimit, name=names[0])
        elif key == ord('4'):
            cmap_image2 = data1.copy()
            cmap_image2[(cmap_image2 < dlimit)] = 0
            cmap_image2[(cmap_image2 > ulimit)] = ulimit
            print_hist_and_graphics(cmap_image2, dlimit, ulimit, name=names[1])
        elif key == ord('z'):
            ulimit = 15000
            dlimit = 5000
            cv2.setTrackbarPos("U", nameWindow, ulimit)
            cv2.setTrackbarPos("D", nameWindow, dlimit)
        elif key == ord('c'):
            auto_contrast(combined_image)
        elif key == ord('e'):
            d = np.array(auto_contrast_cv2(data))
            d1 = np.array(auto_contrast_cv2(data1))
            print_graphics_cv2_arr(d, d1, d.max(), nameWindow="auto")
        elif key == ord('o'):
            ulimit = max_limit
            dlimit = 0
            cv2.setTrackbarPos("U", nameWindow, ulimit)
            cv2.setTrackbarPos("D", nameWindow, dlimit)
        elif key == 44:
            cv2.destroyAllWindows()
            return 1
        elif key == 46:
            cv2.destroyAllWindows()
            return 2


def get_hist_p(data, data1, diff, bins=2000):
    plt.figure(figsize=(10, 10))
    f_data = data.flatten()
    f_data1 = data1.flatten()
    f_diff = diff.flatten()

    clean_data = data.flatten()
    clean_data = clean_data[np.isfinite(clean_data)]
    min_x = np.percentile(clean_data, 1) * 2
    max_x = np.percentile(clean_data, 99) * 2

    clean_data1 = data1.flatten()
    clean_data1 = clean_data1[np.isfinite(clean_data1)]
    min_x1 = np.percentile(clean_data1, 1) * 2
    max_x1 = np.percentile(clean_data1, 99) * 2

    clean_diff = diff.flatten()
    clean_diff = clean_diff[np.isfinite(clean_diff)]
    min_d = np.percentile(clean_diff, 1) * 2
    max_d = np.percentile(clean_diff, 99) * 2

    counts, bin_edges, patches = plt.hist(f_data, bins=bins)
    counts1, bin_edges1, patches1 = plt.hist(f_data1, bins=bins)
    counts_d, bin_edges_d, patches_d = plt.hist(f_diff, bins=bins)

    plt.close()

    return min(min_x, min_x1, 0), max(max_x, max_x1), 0, max(max(counts*1.5), max(counts1*1.5)), min(0, min_d), max_d, max(counts_d*1.5)


def create_hists(data, data1, diff, diff1=None, bins=2000,
                 xmin_data=0, xmax_data=6000, xmin_diff=-1000, xmax_diff=1000, alpha=0.5,
                 ymin_data=0, ymax_data=20000, ymin_diff=0, ymax_diff=30000, show=False,
                 figsize_x=16.54, figsize_y=5.12, return_data=False):
    #15.36
    fig = plt.figure(figsize=(figsize_x, figsize_y))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.65, 1])

    ax1 = fig.add_subplot(gs[0, 0])
    result_hist = ax1.hist(data.flatten(), bins=bins)

    if return_data:
        if show:
            plt.show()
        plt.close()
        return result_hist

    if xmin_data is not None and xmax_data is not None:
        ax1.set_xlim(xmin=xmin_data, xmax=xmax_data)
    if ymin_data is not None and ymax_data is not None:
        ax1.set_ylim(ymin=ymin_data, ymax=ymax_data)

    result_hist1 = ax1.hist(data1.flatten(), bins=bins, alpha=0.5)

    ax2 = fig.add_subplot(gs[0, 1])
    if diff1 is not None:
        result_hist_diff = ax2.hist(diff1.flatten(), bins=bins)
    else:
        alpha = 1
        result_hist_diff = None
    result_hist_diff1 = ax2.hist(diff.flatten(), bins=bins, alpha=alpha, color="orange")


    if xmin_diff is not None and xmax_diff is not None:
        ax2.set_xlim(xmin=xmin_diff, xmax=xmax_diff)
    if ymin_diff is not None and ymax_diff is not None:
        ax2.set_ylim(ymin=ymin_diff, ymax=ymax_diff)

    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.97, top=0.99, wspace=0.13, hspace=0)

    canvas = plt.gcf().canvas
    canvas.draw()
    rgb_string = canvas.buffer_rgba()

    image_array = np.frombuffer(rgb_string, dtype=np.uint8)
    image_array = image_array.reshape(canvas.get_width_height()[::-1] + (4,))

    if show:
        plt.show()
    else:
        plt.close()

    return image_array[:, :, :3]


def create_img_for_video(
        data, data1, name=None, names=None, text_place="t", _type=1, upper_limit=500.,
        lower_limit=None, auto_contrast=True, auto_contrast_percentiles=[2, 98]
):
    ulimit = 10000
    dlimit = 5000
    ulimit_diff = 900
    dlimit_diff = 0
    cmap = plt.get_cmap('gray')

    combined_image = cv2.hconcat([ cv2.resize(data,(512, 512)), cv2.resize(data1,(512, 512))])

    if auto_contrast:
        processed_image, _, _ = auto_contrast_skimage(combined_image, auto_contrast_percentiles=auto_contrast_percentiles)
    else:
        processed_image = combined_image
    cmap_image = np.array(processed_image)

    cmap_image_max = np.max(cmap_image[~np.isnan(cmap_image)])

    cmap_image = drive_to_color_palette(cmap_image, 0, cmap_image_max, cmap)

    if _type == 0: #Gray
        diff = cv2.absdiff(data, data1)

        diff_cmap = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)
        diff_cmap = cv2.cvtColor(diff_cmap, cv2.COLOR_RGB2BGR)
        cmap_image = cv2.cvtColor(cmap_image, cv2.COLOR_GRAY2BGR)


    elif _type == 1: #heat map
        # diff = data.astype(float) - data1.astype(float)
        diff = data - data1
        diff_cmap = save_heat_map(diff, upper_limit=upper_limit, lower_limit=lower_limit)
        diff_cmap = cv2.cvtColor(diff_cmap, cv2.COLOR_RGB2BGR)
        cmap_image = cv2.cvtColor(cmap_image, cv2.COLOR_GRAY2BGR)
        # print(f'gg: {diff_cmap.shape}')
        # print(f'gg1: {cmap_image.shape}')
        #cmap_image = np.hstack((combined_image, diff_cmap))

    elif _type == 2: #abs heat map
        # diff = data.astype(float) - data1.astype(float)
        diff = data - data1

        diff_cmap = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)

        diff_cmap = cv2.cvtColor(diff_cmap, cv2.COLOR_RGB2BGR)
        cmap_image = cv2.cvtColor(cmap_image, cv2.COLOR_GRAY2BGR)

    else:
        return



    # cmap_image = drive_to_color_palette(combined_image, dlimit, ulimit, cmap)

    if names:
        top_border = 50
        bottom_border = 50
        left_border = 0
        right_border = 0

        expanded_image = cv2.copyMakeBorder(cmap_image, top_border, bottom_border, left_border, right_border,
                                            cv2.BORDER_CONSTANT)
        expanded_image_diff = cv2.copyMakeBorder(diff_cmap, top_border, bottom_border, left_border, right_border,
                                                 cv2.BORDER_CONSTANT)

        # print(f'ff: {expanded_image.shape}')
        # print(f'ff1: {expanded_image_diff.shape}')

        #print(data.shape)
        n = data.shape[1] // 14
        text = names[0] + ' ' * n + " " + ' ' * n + names[1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        font_thickness = 1
        text_color = (255, 255, 255)

        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

        if text_place == 'b':
            text_position = ((expanded_image.shape[1] - text_size[0]) // 2, cmap_image.shape[0] + top_border + 30)
        elif text_place == 't':
            text_position = ((expanded_image.shape[1] - text_size[0]) // 2, top_border - 10)
        else:
            text_position = ((expanded_image.shape[1] - text_size[0]) // 2, cmap_image.shape[0] + top_border + 30)

        cv2.putText(expanded_image, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        cv2.putText(expanded_image_diff, "    diff", text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)


        mistake = expanded_image_diff.shape[0] - expanded_image.shape[0]
        #coef = expanded_image.shape[0]/expanded_image_diff[mistake:].shape[0]
        #img = expanded_image_diff[mistake:]
        #resized_img = cv2.resize(expanded_image_diff[mistake:], (int(img.shape[1]*coef), int(img.shape[0]*coef)))

        #print(f'fdsafsa {resized_img.shape, expanded_image.shape}')
        #result = cv2.hconcat([expanded_image, resized_img])
        result = cv2.hconcat([expanded_image, expanded_image_diff[mistake:]])
    else:
        result = cv2.hconcat([cmap_image, diff_cmap])

    if name:
        top_border = 50
        bottom_border = 0
        left_border = 0
        right_border = 0

        # Расширение изображения
        expanded_image = cv2.copyMakeBorder(result, top_border, bottom_border, left_border, right_border,
                                            cv2.BORDER_CONSTANT)

        # Добавление текста
        text = name
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 1
        text_color = (255, 255, 255)  # Цвет текста в формате BGR

        # Определение размера текста для вычисления координат центра
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

        # Определение координат текста в расширенной области
        text_position = ((expanded_image.shape[1] - text_size[0]) // 2, top_border - 10)

        # Нанесение текста на изображение
        cv2.putText(expanded_image, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        return expanded_image

    return result


def cut_img(image, percent_to_trim=0.1, nan=True):
    height, width = image.shape
    radius = min(height, width) // 2

    center = (width // 2, height // 2)
    trim_radius = int(radius * percent_to_trim)

    mask = np.zeros((height, width), dtype=np.uint8)  # Используем тип uint8 для маски

    cv2.circle(mask, center, radius - trim_radius, 255, thickness=cv2.FILLED)  # Заполняем круг значением 255

    if nan:
        result_image = np.where(mask == 255, image, np.nan)  # Используем np.where для создания нового изображения с np.nan вместо 0
    else:
        result_image = np.where(mask == 255, image, 0)
    return result_image


def remove_single_pixels(data, log=False, label_diff_region=False, data_copy_del=False):

    blurred_image = cv2.GaussianBlur(data, (21, 21), 0)  # (5, 5) - размер ядра фильтра, 0 - стандартное отклонение

    diff = data - blurred_image
    cut_diff = cut_img(diff)

    cut1_diff = cut_diff.copy()
    cut1_diff[cut1_diff>60000] = np.nan
    cut1_diff[cut1_diff == np.nan] = False
    #cut1_diff[cut1_diff > 0] = True

    binary_diff = (cut1_diff > 0).astype(bool)

    label_diff = label(binary_diff)

    if log:
        print(f"Count labels on diff: {label_diff.max()}")

    regions = regionprops(label_diff)

    if label_diff_region:
        label_diff_region = label_diff.copy()

    data_copy = np.array(data.copy())

    if data_copy_del:
        data_copy_del = np.array(data.copy())

        for region in regions:
            if region.area < 2.:
                #label_diff_region[label_diff_region == region.label] = 0
                region_coords = region.coords
                for coord in region_coords:
                    data_copy_del[coord[0], coord[1]] = 0.

    for region in regions:
        if region.area < 2.:
            region_coords = region.coords
            #print(region_coords)
            #data_copy[int(region_coords[0]), int(region_coords[1])] = 0.
            for coord in region_coords:
                data_copy[coord[0], coord[1]] = 0.

            def interpolate_neighbours(image, coord):
                interpolated_values = []
                x, y = coord
                neighbours = []
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < image.shape[0] and 0 <= ny < image.shape[1] and (nx, ny) != (x, y):
                            neighbours.append(image[nx, ny])
                if neighbours:
                    interpolated_values.append(np.mean(neighbours))
                else:
                    interpolated_values.append(0)  # Если нет соседей, ставим 0
                return interpolated_values


            # Интерполируем значения для удаленных точек
            interpolated_values = interpolate_neighbours(data_copy, region_coords[0])

            # Запишем интерполированные значения обратно в копию изображения
            data_copy[region_coords[:, 0], region_coords[:, 1]] = interpolated_values

        elif label_diff_region is not False:
            label_diff_region[label_diff_region == region.label] = 0
            #del regions[region.label-1]
    if label_diff_region is not False and data_copy_del is not False:
        return data_copy, label_diff_region, data_copy_del
    if label_diff_region is not False:
        return data_copy, label_diff_region
    if data_copy_del is not False:
        return data_copy, data_copy_del
    return data_copy


def create_correct_matrix(
        count_compression=2,
        base_shape=2048,
        path_file="C:/work/search_for_oxide_cloud/ALL SKY IMAGERS/Calibration SN10210/UNIFORMITY COEFFICIENT FILES/20190718_Russia-LZOS_KEO10210_5577L14002-02_0001000ms_G3_FOV180_uniformity_map_2048x2048.dat"
):
    matrix = np.fromfile(path_file, dtype='float32')

    matrix2048 = np.reshape(matrix, (base_shape, base_shape), order='F')

    new_matrix = matrix2048
    new_shape = base_shape
    for i in range(count_compression):
        new_shape //= 2
        old_matrix = new_matrix
        new_matrix = np.zeros((new_shape, new_shape))

        for i in range(new_shape):  # range(1,uc.shape[0],2):
            for j in range(new_shape):  # range(1,uc.shape[1],2):
                new_matrix[i, j] = np.mean(old_matrix[i*2:i*2+2, j*2:j*2+2])

    return new_matrix


def calculate_frame_Rayleigh(data, info, log=False):
    A = np.float64(file.get_A(info.CCDGAIN, info.ROSPEED, info.DEVICEID))
    B = np.float64(info.BINNING*info.BINNING)
    t_exp = np.float64(info.EXPOSURE[:-2])/1000
    G = 1.

    if log:
        print(f"A={A}, B={B}, t_exp={t_exp}, G={G}")

    data = data.copy()
    data = A * data / B * t_exp * G

    return data


def time_to_seconds(time_str):
    t = datetime.strptime(time_str, '%H:%M:%S')
    return t.hour * 3600 + t.minute * 60 + t.second


# Функция для форматирования времени
def format_time(seconds):
    return str(datetime.utcfromtimestamp(seconds).strftime('%H:%M:%S'))


def data_analysis(path, filename, i_start, i_end, start=0, last_i_start=1, count=3, count_max=5, rgb=True,
                  log=False, x_label="Frame", y_label='Count clusters', title='SLIC DBSCAN'):
    filename = path + filename
    data = []

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines[:-1]:  # Пропустить последнюю строку
            parts = line.strip().split()
            y = float(parts[0])
            i0 = parts[1]
            i1 = parts[2]
            if not rgb:
                i0 = int(parts[3])
                i1 = int(parts[4])
            data.append((y, i0, i1))

    # Преобразование данных в numpy массив
    data = np.array(data)

    # Разделение данных на соответствующие столбцы
    y = data[:, 0].astype(float)
    i0 = data[:, 1].astype(int)
    i1 = data[:, 2].astype(int)
    # i0 = data[:, 3].astype(int)
    # i1 = data[:, 4].astype(int)

    # Построение графика
    plt.figure(figsize=(10, 5))

    if log:
        print(f"y = {y}")

    buf_answer = []
    start_up = 0
    n_up = 0
    last_i = last_i_start

    for i in range(1, len(y)):
        if y[i] >= last_i:
            if n_up == 0:
                start_up = i
            n_up += 1
            last_i = y[i]
        else:
            if n_up >= count and n_up < count_max:
                plt.scatter(start_up + start, y[start_up], color="red", s=50, zorder=2)
                plt.scatter(i + start - 1, last_i, color="pink", s=50, zorder=2)
                buf_answer.append(start_up + start)
            n_up = 0
            last_i = last_i_start

    if log:
        print(f"answer: {buf_answer}")
        print(f"count answer: {len(buf_answer)}")

    # Формирование строк для оси x
    x_labels = [f"{i0[i]}-{i1[i]}" for i in range(len(i0))]

    # Преобразование x_labels в числовые индексы для оси x
    x_indices = np.arange(len(x_labels))

    plt.plot(i0, y, marker='o', linestyle='-', zorder=1)

    # Настройка графика
    # plt.xlabel('time')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)

    # Установка меток только для каждой 5-й засечки
    indices = np.arange(0, len(x_labels), 10)
    plt.xticks(i0[indices], [x_labels[i] for i in indices], rotation=45)

    # plt.xticks(i0, x_labels, rotation=45)

    # Форматирование оси x как числовой
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: int(x)))

    # Закрашивание области, где i0 > 120 и i0 < 125
    for idx in range(len(i0)):
        if i_start < i0[idx] < i_end:
            plt.axvspan(idx - 0.5, idx + 0.5, color='yellow', alpha=0.3)

    # Показать график
    plt.tight_layout()  # Для лучшего размещения меток осей

    plt.show()


def datas_analysis(
        path, i_start=120, i_end=125,
        files=[
            'count_GM.txt', 'count_DBSCAN.txt', 'count_Kmean.txt',
            'count_HDBSCAN.txt', 'count_SLIC_DBSCAN.txt'
        ],
        rgb=True, x_label='time', y_label='count clusters', title='Comparison of algorithms'
):
    # Функция для чтения данных из файла
    def read_data(filename):
        data = []
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines[:-1]:  # Пропустить последнюю строку
                parts = line.strip().split()
                y = float(parts[0])
                x0 = parts[1]
                x1 = parts[2]
                i0 = float(parts[3])
                i1 = float(parts[4])
                data.append((y, x0, x1, i0, i1))
        return np.array(data)

    # Чтение данных из каждого файла
    all_data = []
    for file in files[:-1]:
        data = read_data(path + file)
        all_data.append(data)

    # Построение графиков для каждого набора данных
    plt.figure(figsize=(12, 6))

    for idx, data in enumerate(all_data):
        # Разделение данных на соответствующие столбцы
        y = data[:, 0].astype(float)
        x0 = data[:, 1]
        x1 = data[:, 2]
        i0 = data[:, 3].astype(float)
        i1 = data[:, 4].astype(float)

        # Формирование строк для оси x
        x_labels = [f"{x0[i]}-{x1[i]}" for i in range(len(x0))]

        # Построение графика
        plt.plot(i0, y, marker='o', linestyle='-', label=f'{files[idx][6:-4]}')

        # Закрашивание области, где i0 > 120 и i1 < 125
        for idx in range(len(i0)):
            if i_start < i0[idx] < i_end:
                plt.axvspan(i0[idx] - 0.5, i0[idx] + 0.5, color='yellow', alpha=0.3)

    # Установка меток оси x по данным i0 и подписей относительно x0 с шагом 5 по i0
    # Определим шаг для меток оси x
    step = 5
    # Создадим список индексов для меток оси x
    ticks = np.arange(0, len(x_labels), step)
    # Создадим список подписей для оси x, используя x0
    labels = [x0[i] for i in ticks]
    # Установим метки и подписи оси x
    plt.xticks(ticks, labels, rotation=45)

    # Показать график
    plt.tight_layout()

    path = r"C:\\work\\search_for_oxide_cloud\SfOC\\result\\KEO\\2014\\30"
    # filename =  path + '\\count_SLIC_DBSCAN.txt'
    filename = path + '\\' + files[-1]
    data = []

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines[:-1]:  # Пропустить последнюю строку
            parts = line.strip().split()
            y = float(parts[0])
            i0 = parts[1]
            i1 = parts[2]
            if not rgb:
                i0 = int(parts[3])
                i1 = int(parts[4])
            data.append((y, i0, i1))

    # Преобразование данных в numpy массив
    data = np.array(data)

    # Разделение данных на соответствующие столбцы
    y = data[:, 0].astype(float)
    i0 = data[:, 1].astype(int)
    i1 = data[:, 2].astype(int)

    # Формирование строк для оси x
    x_labels = [f"{i0[i]}-{i1[i]}" for i in range(len(i0))]

    # Преобразование x_labels в числовые индексы для оси x
    x_indices = np.arange(len(x_labels))

    plt.plot(i0, y, marker='o', linestyle='-', zorder=4, label=f'SLIC_DBSCAN')

    # Настройка графика
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    plt.legend()

    plt.show()


def hist_3d(names, new_path, file_number, end=10, name_g="", xlim3d_min=0, xlim3d_max=None, ylim3d_min=0, ylim3d_max=None,
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
        data_cut = cut_img(data)

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


def hist_3d_diff(names, new_path, file_number, end=10, name_g="", xlim3d_min=0, xlim3d_max=None, ylim3d_min=0, ylim3d_max=None,
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
        data_cut = cut_img(data)

        name_path1 = os.path.join(new_path, names[i + 1])
        info1, data1 = file.open_gz(name_path1)
        data_cut1 = cut_img(data1)

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

