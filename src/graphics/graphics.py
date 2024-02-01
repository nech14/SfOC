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


def print_graphics_cv2_arr(data, data1, max_limit=255, dlimit=0):
    combined_image = cv2.hconcat([data, data1])

    ulimit = max_limit
    dlimit = 0

    result_flag = False

    def uupdate(value):
        nonlocal ulimit
        ulimit = value

    def dupdate(value):
        nonlocal dlimit
        dlimit = value

    cv2.namedWindow("GraphicData", cv2.WINDOW_KEEPRATIO)

    cv2.createTrackbar("U", "GraphicData", ulimit, max_limit, uupdate)
    cv2.createTrackbar("D", "GraphicData", dlimit, max_limit, dupdate)

    cmap = plt.get_cmap('gray')

    while True:
        cmap_image = drive_to_color_palette(combined_image, dlimit, ulimit, cmap)

        cv2.imshow("GraphicData", cmap_image)

        if result_flag:
            cmap_image1 = drive_to_color_palette(data, dlimit, ulimit, cmap)

            cmap_image2 = drive_to_color_palette(data1, dlimit, ulimit, cmap)

            diff = cv2.absdiff(cmap_image1, cmap_image2)
            cv2.imshow("GraphicDiff", diff)

            if cv2.waitKey(1) == ord('h'):
                print_hist_and_graphics(diff, dlimit, ulimit)

        if cv2.waitKey(1) == ord('q'):
            break

        if cv2.waitKey(1) == ord('g'):
            result_flag = not result_flag
            if not result_flag:
                cv2.destroyWindow("GraphicDiff")

        if cv2.waitKey(1) == ord('1'):
            if not result_flag:
                cmap_image1 = drive_to_color_palette(data, dlimit, ulimit, cmap)
            print_hist_and_graphics(cmap_image1, dlimit, ulimit)

        if cv2.waitKey(1) == ord('2'):
            if not result_flag:
                cmap_image2 = drive_to_color_palette(data1, dlimit, ulimit, cmap)
            print_hist_and_graphics(cmap_image2, dlimit, ulimit)