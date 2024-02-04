import matplotlib.pyplot as plt
import numpy as np
import cv2


def print_graphics(data):
    plt.figure()
    plt.subplot(121)
    plt.imshow(data, origin='lower', cmap='gray')
    plt.subplot(122)
    plt.imshow(data, origin='lower')
    plt.show()


def save_graphics(data, path, name):
    fig = plt.figure(figsize=(20, 10))

    plt.subplot(121)
    plt.imshow(data, origin='lower', cmap='gray')
    plt.subplot(122)
    plt.imshow(data, origin='lower')
    plt.savefig(path + '/' + name + '.png')
    plt.close()


def print_hist_and_graphics(data, vmin=5000, vmax=15000):
    plt.figure()
    plt.subplot(121)
    histogram = plt.hist(data.flatten(), bins='auto')
    plt.subplot(122)
    plt.imshow(data, cmap='gray', vmin=vmin, vmax=vmax)
    plt.colorbar()

    plt.show()


def drive_to_color_palette(combined_image, dlimit, ulimit, cmap):
    cmap_image = np.clip(combined_image, dlimit, ulimit)
    cmap_image = (cmap_image - dlimit) / (ulimit - dlimit)  # Нормализация значений
    cmap_image = (cmap_image * 255).astype(np.uint8)  # Конвертация в формат uint8

    # Применение цветовой карты
    cmap_image = cmap(cmap_image)

    # Преобразование в BGR (OpenCV использует формат BGR)
    cmap_image = (cmap_image[:, :, :3] * 255).astype(np.uint8)
    return cmap_image


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


def print_graphics_cv2_arr(data, data1, max_limit=255, dlimit=0, names=['1', '2']):
    combined_image = cv2.hconcat([data, data1])

    ulimit = max_limit
    dlimit = 0
    ulimit_diff = max_limit
    dlimit_diff = 0

    result_flag = False

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

    cv2.namedWindow("GraphicData", cv2.WINDOW_KEEPRATIO)

    cv2.createTrackbar("U", "GraphicData", ulimit, max_limit, uupdate)
    cv2.createTrackbar("D", "GraphicData", dlimit, max_limit, dupdate)

    cmap = plt.get_cmap('gray')

    p_flag = True
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

        cv2.imshow("GraphicData", cmap_image)

        key = cv2.waitKey(1)

        if result_flag:
            #cmap_image1 = drive_to_color_palette(data, dlimit, ulimit, cmap)
            cmap_image1 = data.copy()
            cmap_image1[(cmap_image1 < dlimit) | (cmap_image1 > ulimit)] = 0

            #cmap_image2 = drive_to_color_palette(data1, dlimit, ulimit, cmap)
            cmap_image2 = data1.copy()
            cmap_image2[(cmap_image2 < dlimit) | (cmap_image2 > ulimit)] = 0

            diff = cv2.absdiff(cmap_image1, cmap_image2)

            diff1 = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)

            cv2.imshow("GraphicDiff", diff1)

            if key == ord('h'):
                print_hist_and_graphics(diff, dlimit_diff, ulimit_diff)

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
            print_hist_and_graphics(data, dlimit, ulimit)
        elif key == ord('2'):
            print_hist_and_graphics(data1, dlimit, ulimit)
        elif key == ord('3'):
            cmap_image1 = data.copy()
            cmap_image1[(cmap_image1 < dlimit) | (cmap_image1 > ulimit)] = 0
            print_hist_and_graphics(cmap_image1, dlimit, ulimit)
        elif key == ord('4'):
            cmap_image2 = data.copy()
            cmap_image2[(cmap_image2 < dlimit) | (cmap_image2 > ulimit)] = 0
            print_hist_and_graphics(cmap_image2, dlimit, ulimit)
        elif key == 44:
            cv2.destroyAllWindows()
            return 1
        elif key == 46:
            cv2.destroyAllWindows()
            return 2