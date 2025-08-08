import os

import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image


def create_mp4(
        frames,
        name="output",
        flag_info=False,
        save_folder="",
        fps=1,
        frames_s=1,
        logfun=None
):
    # Размеры кадра и частота кадров в видео
    frame = frames[0]
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    if len(save_folder) > 0 and not os.path.exists(save_folder):
        # Если папки не существует, создаем её
        os.makedirs(save_folder)

    # Создаем объект VideoWriter для записи видео в формате MP4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f"{save_folder}/{name}.mp4", fourcc, fps, (frame_width, frame_height))
    count = 0
    for i in frames:
        for j in range(frames_s):
            out.write(i)

        count += 1
        if flag_info:
            print(f"create video: {count}/{len(frames)}")
        if not logfun is None:
            logfun("create video", count, len(frames))

    # Закрываем объект VideoWriter
    out.release()


def save_heat_map(
        data_heat,
        upper_limit=500.,
        lower_limit=None,
        save_folder=None,
        file_name=None,
        nameFile="diff",
        color_bar=True
):
    if lower_limit is None:
        lower_limit = -upper_limit

    fig, ax = plt.subplots(figsize=(8, 8))
    mask = np.ma.masked_equal(data_heat, 0)
    plt.imshow(mask, cmap="RdBu_r", interpolation='nearest', vmin=lower_limit, vmax=upper_limit)
    if color_bar:
        cbar = plt.colorbar(shrink=0.8, fraction=0.1)
        for text in cbar.ax.get_yticklabels():
            text.set_color('white')
    plt.axis('off')
    fig.set_facecolor('black')

    canvas = plt.gcf().canvas
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


    return image_array