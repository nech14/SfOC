import os

import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.file import file
from src.graphics import graphics, auto_contrast_skimage
from src.models.imges.abstract_img import AbstractImg
from src.models.imges.duo_img_model import DuoImg
from src.models.imges.img_model import Img
from src.models.recipes.base_recipes_model import BaseRecipes
from src.models.recipes.hearmap_recipe_model import HeatmapRecipe
from src.models.recipes.image_recipe_model import ImageRecipe
from src.models.recipes.video_recipe_model import VideoRecipe


def get_image(recipe: ImageRecipe) -> Img:
    if recipe.names_files is None or len(recipe.names_files) == 0:
        recipe.get_names_files()
    name_path = os.path.join(recipe.root_path, recipe.names_files[recipe.frame_number])
    info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
    return Img(data, recipe.fit_format(info))

def get_images_path(recipe: HeatmapRecipe) -> list[str]:
    if recipe.names_files is None or len(recipe.names_files) == 0:
        recipe.get_names_files()
    return recipe.names_files

def get_images_by_number(recipe: BaseRecipes, number: int) -> Img:
    if recipe.names_files is None or len(recipe.names_files) == 0:
        recipe.get_names_files()
    name_path = os.path.join(recipe.root_path, recipe.names_files[number])
    info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
    return Img(data, recipe.fit_format(info))

def use_dark_frames_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.dark:
        if recipe.dark_start is None or recipe.dark_start is None:
            recipe.open_dark()
        img.dark_frames(recipe.dark_start, recipe.dart_end)

def remove_single_pixels_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.remove_single_pixels:
        img.remove_single_pixels()

def correct_matrix_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if not recipe.correct_matrix_path is None:
        if recipe.correct_matrix is None:
            recipe.open_correct_matrix()
        img.correct_matrix(recipe.correct_matrix, recipe.multiplication_on_correct_matrix)

def rayleigh_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.rayleigh:
        img.rayleigh()

def cut_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.cut:
        img.cut(percent_to_trim=recipe.percent_to_trim)

def auto_contrast_image(recipe: BaseRecipes, img: AbstractImg) -> list:
    if recipe.auto_contrast:
        return img.auto_contrast_version(recipe.auto_contrast_percentiles)
    return img.data

def auto_contrast_result(recipe: HeatmapRecipe, img) -> list:
    if recipe.result_auto_contrast:
        result, _, _ = auto_contrast_skimage(img, auto_contrast_percentiles=[2, 98])
        return result
    return img

def show_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.show:
        img.show(recipe)

def save_result_matrix_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.result_matrix_save_folder is None:
        return

    if recipe.result_matrix_save_folder == "" and not recipe.save_folder is None and recipe.save_folder != "":
        recipe.result_matrix_safe_folder = os.path.join(recipe.save_folder, "result_matrix")

    img.save_rayleigh_matrix(folder=recipe.result_matrix_safe_folder, filename=recipe.file_name)


def save_image(recipe: ImageRecipe, processed_image) -> None:
    if not os.path.exists(recipe.save_folder):
        os.makedirs(recipe.save_folder)

    plt.title(f"{recipe.name}")

    plt.figure(figsize=recipe.figsize, dpi=100)
    plt.imshow(processed_image, cmap="gray")
    plt.gca().invert_yaxis()
    plt.axis('off')
    if recipe.file_name is None:
        file_name_buf = recipe.names_files[recipe.frame_number]
    else:
        file_name_buf = recipe.file_name
    plt.savefig(recipe.save_folder + f"/{file_name_buf}.png", bbox_inches='tight')
    plt.close()



def create_hist(recipe: HeatmapRecipe, img: Img):
    if recipe.xmax_data is None or recipe.xmin_data is None:
        recipe.found_limits()

    # bins = range(0, 10000, 100)
    # bins = np.linspace(recipe.xmin_data, recipe.xmax_data, recipe.bins-2)
    bins = np.linspace(0, recipe.xmax_data, recipe.bins)
    # bins = np.insert(bins, 0 ,0)
    # bins = np.append(bins, 800000)


    hist, _, _ = graphics.create_hists(
        img.data, img.data, img.data, bins=bins,
        return_data=True, show=False)

    return hist

def save_heatmap_image(recipe: HeatmapRecipe, transposed_data, info_for_heatmap, show=False):
    plt.figure(figsize=recipe.figsize, dpi=100)

    if not recipe.name is None and recipe.name != "":
        plt.title(recipe.name)

    plt.imshow(transposed_data, cmap=recipe.cmap, aspect='auto')
    colorbar = plt.colorbar()
    colorbar.set_label('n in bin')

    y_positions = np.linspace(0, transposed_data.shape[0] - 1, 10)  # Позиции меток на графике
    y_labels = np.linspace(recipe.xmin_data, recipe.xmax_data, 10)

    plt.yticks(y_positions, [int(label) for label in y_labels], fontsize=8)  # Устанавливаем метки
    plt.ylabel("y")
    plt.gca().invert_yaxis()

    plt.xlabel("time")
    plt.xticks(np.arange(0, len(info_for_heatmap), 10), info_for_heatmap[::10], rotation=45, ha='right', fontsize=8)

    name_file = recipe.file_name
    if name_file is None:
        name_file = recipe.name

    if not recipe.save_folder is None:
        if not os.path.exists(recipe.save_folder):
            # Если папки не существует, создаем её
            os.makedirs(recipe.save_folder)
        plt.savefig(recipe.save_folder + f'/{name_file}.png')

    if show:
        plt.show()
    plt.close()


def create_image_with_hist(recipe: VideoRecipe, duo_img: DuoImg, diff_last=None) -> DuoImg:
    if not recipe.hist:
        return duo_img

    img = duo_img.view_data

    data = duo_img.img_first.data.copy()
    data1 = duo_img.img_second.data.copy()

    diff = data - data1

    if (recipe.xmax_data is None or recipe.xmin_data is None or
        recipe.ymax_data is None or recipe.ymin_data is None):
        recipe.found_limits()

    img_hist = graphics.create_hists(data, data1, diff, diff_last, figsize_x=(img.shape[1] + 0.5) / 100,
                                     figsize_y=img.shape[0] / 100,
                                     xmin_data=recipe.xmin_data, xmax_data=recipe.xmax_data, xmin_diff=recipe.xmin_diff, xmax_diff=recipe.xmax_diff,
                                     ymin_data=recipe.ymin_data, ymax_data=recipe.ymax_data, ymin_diff=0, ymax_diff=recipe.ymax_diff,
                                     bins=recipe.bins)
    img_hist_BGR = cv2.cvtColor(img_hist, cv2.COLOR_RGB2BGR)
    duo_img.view_data = cv2.vconcat([img, img_hist_BGR])
    return duo_img

def create_base_img_for_video(recipe: VideoRecipe, duo_img: DuoImg) -> DuoImg:
    duo_img.view_data = graphics.create_img_for_video(
        duo_img.img_first.data,
        duo_img.img_second.data,
        name=recipe.name, _type=1,
        names=[f"{duo_img.img_first.fit_format.get_datetime()}", f"{duo_img.img_second.fit_format.get_datetime()}"],
        upper_limit=500., lower_limit=None, auto_contrast=recipe.auto_contrast,
        auto_contrast_percentiles=recipe.auto_contrast_percentiles
    )
    return duo_img


def save_image_for_video(recipe: VideoRecipe, duo_img: DuoImg) -> None:
    if recipe.save_folder is None:
        return

    if not os.path.exists(recipe.save_folder):
        # Если папки не существует, создаем её
        os.makedirs(recipe.save_folder)
    img = cv2.cvtColor(duo_img.view_data, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=recipe.figsize, dpi=500)
    plt.imshow(img)
    plt.axis('off')
    # plt.savefig(save_folder + f"/{i}.png", bbox_inches='tight')
    if recipe.frame_name is None:
        file_name_buf = f"{duo_img.img_first.fit_format.get_datetime()}".replace(":", "-")
    else:
        file_name_buf = recipe.frame_name
    plt.savefig(recipe.save_folder + f"/{file_name_buf}.png", bbox_inches='tight')
    plt.close()
