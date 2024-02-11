import matplotlib.pyplot as plt
import numpy as np
import cv2
from skimage.measure import label
from skimage import exposure


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
    cmap_image = np.clip(combined_image, dlimit, ulimit)
    cmap_image = (cmap_image - dlimit) / (ulimit - dlimit)  # Нормализация значений
    cmap_image = (cmap_image * 255).astype(np.uint8)  # Конвертация в формат uint8

    # Применение цветовой карты
    cmap_image = cmap(cmap_image)

    # Преобразование в BGR (OpenCV использует формат BGR)
    cmap_image = (cmap_image[:, :, 0] * 255).astype(np.uint8)
    return cmap_image[:, :]

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


def auto_contrast_skimage(data):
    image = data.copy()
    non_zero_values = image[image > 0]
    p2, p98 = np.percentile(non_zero_values, (2, 98))
    result = exposure.rescale_intensity(image, in_range=(p2, p98))
    return result


def auto_contrast_cv2(data):
    image = data.copy()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(10, 10))
    result = clahe.apply(image)
    return result


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
                #cmap_image1 = drive_to_color_palette(data, dlimit, ulimit, cmap)
                cmap_image1 = data.copy()
                cmap_image1[(cmap_image1 < dlimit) | (cmap_image1 > ulimit)] = 0

                #cmap_image2 = drive_to_color_palette(data1, dlimit, ulimit, cmap)
                cmap_image2 = data1.copy()
                cmap_image2[(cmap_image2 < dlimit) | (cmap_image2 > ulimit)] = 0

                diff = cv2.absdiff(cmap_image1, cmap_image2)

            diff_cmap = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)
            #diff_cmap = auto_contrast_cv2(diff)

            cv2.imshow("GraphicDiff", diff_cmap)

            if key == ord('h'):
                #f_diff = diff.copy()
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
            print_hist_and_graphics(data, dlimit, ulimit, name=names[0])
        elif key == ord('2'):
            print_hist_and_graphics(data1, dlimit, ulimit, name=names[1])
        elif key == ord('3'):
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


def create_img_for_video(data, data1, name=None):
    ulimit = 10000
    dlimit = 5000
    ulimit_diff = 900
    dlimit_diff = 0
    cmap = plt.get_cmap('gray')

    combined_image = cv2.hconcat([data, data1])

    diff = cv2.absdiff(data, data1)

    diff_cmap = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)

    #cmap_image = drive_to_color_palette(combined_image, dlimit, ulimit, cmap)
    cmap_image = np.array(auto_contrast_skimage(combined_image))
    cmap_image = drive_to_color_palette(cmap_image, 0, cmap_image.max(), cmap)

    result = cv2.hconcat([cmap_image, diff_cmap])

    if name:
        top_border = 50
        bottom_border = 50
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
        text_position = ((expanded_image.shape[1] - text_size[0]) // 2, top_border-10)

        # Нанесение текста на изображение
        cv2.putText(expanded_image, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        return expanded_image

    return result


def cut_img(image, percent_to_trim=0.1):
    height, width = image.shape
    radius = min(height, width) // 2

    center = (width // 2, height // 2)
    trim_radius = int(radius * percent_to_trim)

    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, center, radius - trim_radius, (255, 255, 255), thickness=-1)

    result_image = cv2.bitwise_and(image, image, mask=mask)
    return result_image
