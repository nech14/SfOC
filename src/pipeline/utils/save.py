import os

import cv2


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
