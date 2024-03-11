
from src import graphics
from src import file
from src import GUI
import os

import cv2
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


file_number = 11


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


def create_img_for_video(names_files, start_i=0, end_i=None, flag_info=False, name=None, cut=False,
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
                                     names=names, save_folder=(save_folder+'/'+name_img_folder))
    else:
        datas = create_img_for_video(names_files, start_i=start_i, end_i=end_i, flag_info=flag_info, name=name, cut=cut,
                                 names=names)

    if save_folder_vide is None:
        save_folder_vide = save_folder + "/" + name_video_folder
    create_mp4(dates=datas, name=name_file, flag_info=flag_info, save_folder=save_folder_vide)


def viewing_pictures(names, file_number):
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


def create_heatmap(names, new_path, edges=0, start_file=0, end_file=None, log_info=False, title=None, bins=100, auto_contrast=True, cmap="viridis", save_folder="", limit=None):
    if end_file is None:
        end_file = len(names)

    if log_info:
        print('start create heatmap')
    count_files = end_file - start_file - edges*2
    data_for_heatmap = [0] * count_files
    info_for_heatmap = [0] * count_files
    count = 0
    for i in range(start_file+edges, end_file-edges):
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
    #plt.show()
    if log_info:
        print(f"create heatmap: {title}")

current_directory = os.getcwd()

path = os.path.join(current_directory, "data", "ASI0", "2023", "10", "11")
# "data.ASI0.2023.10.11.5577"
# name="data.ASI0.2024.01.12.5577", name_file="data.ASI0.2024.01.12.5577"
#path = os.path.join(current_directory, "data", "ASI0", "2024", "01", "12")
new_path = os.path.join(path, "5577")

names = file.get_name_file(new_path)
print(names)


#viewing_pictures(names, file_number)

create_heatmap(names, new_path, bins=100, edges=0, log_info=True, auto_contrast=False,
               title="data.ASI0.2023.10.11.5577.viridis.100bins_limit_10000_0",
               limit=10000, cmap='viridis', save_folder="result/ASI0/2023/10/11/5577")

#graphics.print_graphics_cv2(combined_image, combined_image.max())


#GUI.start()




#result = create_img_for_video(names, 13, 14, name="GG", cut=True, names=True)
#plt.imshow(result[0])
#plt.show()

#create_video(names, start_i=0, flag_info=True, names=True, name_file="data.ASI0.2023.10.11.5577.heatmap", name="data.ASI0.2023.10.11.5577", cut=True, save_folder="result/ASI0/2023/10/11/5577", save_img=True)


# import joypy
#
# import pandas as pd
# import numpy as np
# from matplotlib import pyplot as plt
# from matplotlib import cm
#
#
# temp = pd.read_csv("data/daily_temp.csv",comment="%")
#
# labels=[y if y%10==0 else None for y in list(temp.Year.unique())]
# fig, axes = joypy.joyplot(temp, by="Year", column="Anomaly", labels=labels, range_style='own',
#                           grid="y", linewidth=1, legend=False, figsize=(6,5),
#                           title="Global daily temperature 1880-2014 \n(°C above 1950-80 average)",
#                           colormap=cm.autumn_r)
#
# plt.show()



def hist_3d(names, file_number, end=10, name_g="", xlim3d_min=0, xlim3d_max=None, ylim3d_min=0, ylim3d_max=None,rotate=False, x_agnes_end=130, y_agnes_end=90, start_folder="result", save_folder="img"):

    #histogram = plt.hist(data_cut.flatten(), bins='auto')
   # print(histogram)
    #plt.show()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection="3d")
    my_cmap = plt.cm.inferno

    count_files = len(names)-end

    for i in range(file_number, count_files):
        # we create evenly spaced bins between the minimum and maximum of the entire dataframe
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path)
        data_cut = graphics.cut_img(data)

        #non_zero_data_cut = data_cut[data_cut != 0]

        histvals, _ = np.histogram(data_cut.flatten(), bins="auto")
        histvals = histvals[1:]

        xbins = np.linspace(data_cut.flatten().min().min(), data_cut.flatten().max().max(), len(histvals)+1)
        # and calculate the center and widths of the bars
        xcenter = np.convolve(xbins, np.ones(2), "valid") / 2
        xwidth = np.diff(xbins)

        # print(xbins)
        # print(xcenter)


        ax.bar(left=xcenter, height=histvals, width=xwidth, zs=(i-file_number)/100, zdir="y", alpha=0.666, linewidth=0.3, color=my_cmap((i-file_number)/(count_files-file_number)))

        print(f"{i-file_number}/{count_files-file_number}")


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
        if not os.path.exists(start_folder+'/'+save_folder):
            # Если не существует, создаем папку
            os.makedirs(start_folder+'/'+save_folder)
        for angle in range(0, x_agnes_end):
            ax.view_init(0, angle)
            print(f"rotate_x: {angle}/{x_agnes_end}")
            #plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle) + '.png')
            #plt.pause(.001)

        for angle in range(0, y_agnes_end):
            ax.view_init(angle, x_agnes_end)
            print(f"rotate_y: {angle}/{y_agnes_end}")
            #plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle+x_agnes_end) + '.png')
            #plt.pause(.001)

    #plt.show()



def hist_3d_diff(names, file_number, end=10, name_g="", xlim3d_min=0, xlim3d_max=None, ylim3d_min=0, ylim3d_max=None,rotate=False, x_agnes_end=130, y_agnes_end=90, start_folder="result", save_folder="diff"):

    #histogram = plt.hist(data_cut.flatten(), bins='auto')
   # print(histogram)
    #plt.show()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection="3d")
    my_cmap = plt.cm.inferno

    count_files = len(names)-end - 1

    for i in range(file_number, count_files):
        # we create evenly spaced bins between the minimum and maximum of the entire dataframe
        name_path = os.path.join(new_path, names[i])
        info, data = file.open_gz(name_path)
        data_cut = graphics.cut_img(data)

        name_path1 = os.path.join(new_path, names[i+1])
        info1, data1 = file.open_gz(name_path1)
        data_cut1 = graphics.cut_img(data1)

        h_diff = data_cut.astype(float) - data_cut1.astype(float)
        #non_zero_data_cut = data_cut[data_cut != 0]

        h_diff = h_diff[h_diff != 0]

        histvals, _ = np.histogram(h_diff.flatten(), bins="auto")
        histvals = histvals[1:]

        xbins = np.linspace(data_cut.flatten().min().min(), data_cut.flatten().max().max(), len(histvals)+1)
        # and calculate the center and widths of the bars
        xcenter = np.convolve(xbins, np.ones(2), "valid") / 2
        xwidth = np.diff(xbins)

        # print(xbins)
        # print(xcenter)


        ax.bar(left=xcenter, height=histvals, width=xwidth, zs=(i-file_number)/100, zdir="y", alpha=0.666, linewidth=0.3, color=my_cmap((i-file_number)/(count_files-file_number)))

        print(f"{i-file_number}/{count_files-file_number}")


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
        if not os.path.exists(start_folder+'/'+save_folder):
            # Если не существует, создаем папку
            os.makedirs(start_folder+'/'+save_folder)
        for angle in range(0, x_agnes_end):
            ax.view_init(0, angle)
            print(f"rotate_x: {angle}/{x_agnes_end}")
            #plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle) + '.png')
            #plt.pause(.001)

        for angle in range(0, y_agnes_end):
            ax.view_init(angle, x_agnes_end)
            print(f"rotate_y: {angle}/{y_agnes_end}")
            #plt.draw()
            plt.savefig(start_folder + '/' + save_folder + '/rotanim_' + str(angle+x_agnes_end) + '.png')
            #plt.pause(.001)

    #plt.show()


def create_video_hist_3d(name_file=None, folder_name="result/ASI0/2023/10/11/OH1", save_folder='video'):
    if name_file is None:
        name_file = folder_name

    if not os.path.exists(folder_name + '/' + save_folder):
        # Если не существует, создаем папку
        os.makedirs(folder_name + '/../' + save_folder)

    # Размеры кадра и частота кадров в видео
    date1 = plt.imread(folder_name+f'/rotanim_{0}.png')
    frame_width = date1.shape[1]
    frame_height = date1.shape[0]
    fps = 5
    # Создаем объект VideoWriter для записи видео в формате MP4
    fourcc1 = cv2.VideoWriter_fourcc(*'mp4v')
    out1 = cv2.VideoWriter(folder_name + '/../' + save_folder + '/' + name_file + ".mp4", fourcc1, fps, (frame_width, frame_height))

    count = 0
    for i in range(1, 220):
        frame = cv2.imread(folder_name + f'/rotanim_{i}.png')
        out1.write(frame)
        if True:
            count += 1
            print(f"create video: {count}/221")

    # Закрываем объект VideoWriter
    out1.release()



#hist_3d(names, file_number, len(names)-20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=0.5, rotate=True)
#hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=1.5, rotate=True)
#hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.OH", xlim3d_max=20000, ylim3d_max=(len(names)-file_number-20)//100, rotate=True, start_folder="result/ASI0/2023/10/11/OH")


#hist_3d(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577", ylim3d_max=(len(names)-file_number)/100, rotate=True, start_folder="result/ASI0/2023/10/11/5577")

#create_video_hist_3d(name_file="result_ASI0_2023_10_11_OH", folder_name="result/ASI0/2023/10/11/OH/img")


#hist_3d_diff(names, file_number, 20, name_g="data.ASI0.2023.10.11.5577.diff", ylim3d_max=(len(names)-file_number)/100, rotate=True, start_folder="result/ASI0/2023/10/11/5577")

#create_video_hist_3d(name_file="result_ASI0_2023_10_11_5577_diff", folder_name="result/ASI0/2023/10/11/5577/diff")

print('hay')
