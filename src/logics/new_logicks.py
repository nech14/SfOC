import os
import pickle

import matplotlib.pyplot as plt
import numpy as np

from src import file
from src.file import FitsInfo
from src.graphics import graphics, auto_contrast_skimage
from src.models.recipes.base_recipes_model import BaseRecipes
from src.models.recipes.hearmap_recipe_model import HeatmapRecipe
from src.models.recipes.image_recipe_model import ImageRecipe
from src.models.imges.img_model import Img
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

def use_dark_frames_image(recipe: BaseRecipes, img: Img) -> None:
    if recipe.dark:
        if recipe.dark_start is None or recipe.dark_start is None:
            recipe.open_dark()
        img.dark_frames(recipe.dark_start, recipe.dart_end)

def remove_single_pixels_image(recipe: BaseRecipes, img: Img) -> None:
    if recipe.remove_single_pixels:
        img.remove_single_pixels()

def correct_matrix_image(recipe: BaseRecipes, img: Img) -> None:
    if not recipe.correct_matrix_path is None:
        if recipe.correct_matrix is None:
            recipe.open_correct_matrix()
        img.correct_matrix(recipe.correct_matrix, recipe.multiplication_on_correct_matrix)

def rayleigh_image(recipe: BaseRecipes, img: Img) -> None:
    if recipe.rayleigh:
        img.rayleigh()

def cut_image(recipe: BaseRecipes, img: Img) -> None:
    if recipe.cut:
        img.cut(percent_to_trim=recipe.percent_to_trim)

def auto_contrast_image(recipe: BaseRecipes, img: Img) -> list:
    if recipe.auto_contrast:
        return img.auto_contrast_version(recipe.auto_contrast_percentiles)
    return img.data

def auto_contrast_result(recipe: HeatmapRecipe, img) -> list:
    if recipe.result_auto_contrast:
        result, _, _ = auto_contrast_skimage(img, auto_contrast_percentiles=[2, 98])
        return result
    return img

def save_result_matrix_image(recipe: BaseRecipes, img: Img) -> None:
    if recipe.result_matrix_save_folder is None:
        return

    if recipe.result_matrix_save_folder == "" and not recipe.save_folder is None and recipe.save_folder != "":
        recipe.result_matrix_safe_folder = os.path.join(recipe.save_folder, "result_matrix")

    if not os.path.exists(recipe.result_matrix_save_folder):
        os.makedirs(recipe.result_matrix_save_folder)

    result_matrix_safe_folder_data = (
        os.path.join(
            recipe.result_matrix_save_folder, f"{recipe.names_files[recipe.frame_number]}.pkl"
        )
    )

    with open(result_matrix_safe_folder_data, 'wb') as file:
        pickle.dump(img.data, file)


def save_image(recipe: ImageRecipe, processed_image) -> None:
    if not os.path.exists(recipe.save_folder):
        # Если папки не существует, создаем её
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


def create_image(recipe: ImageRecipe) -> None:
    img = get_image(recipe)

    remove_single_pixels_image(recipe, img)
    use_dark_frames_image(recipe, img)
    correct_matrix_image(recipe, img)
    rayleigh_image(recipe, img)
    cut_image(recipe, img)
    save_result_matrix_image(recipe, img)
    auto_contrast_image(recipe, img)

    save_image(recipe, img.view_data)
    plt.imshow(img.view_data, cmap="gray")
    plt.gca().invert_yaxis()
    plt.show()


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


def _create_column_for_heatmap(recipe: HeatmapRecipe, img: Img):
    remove_single_pixels_image(recipe, img)
    use_dark_frames_image(recipe, img)
    correct_matrix_image(recipe, img)
    rayleigh_image(recipe, img)
    cut_image(recipe, img)
    auto_contrast_image(recipe, img)

    hist = create_hist(recipe, img)
    return hist


def create_heatmap(recipe: HeatmapRecipe) -> None:
    data_for_heatmap = []
    info_for_heatmap = []

    for frame_id in range(recipe.first_frame_number+recipe.edges, recipe.last_frame_number-recipe.edges):
        img = get_images_by_number(recipe, frame_id)

        hist = _create_column_for_heatmap(recipe, img)
        data_for_heatmap.append(hist)
        info_for_heatmap.append(img.fit_format.get_datetime().time())

    data_for_heatmap = np.array(data_for_heatmap)
    transposed_data = np.transpose(data_for_heatmap)
    transposed_data = auto_contrast_result(recipe, transposed_data)
    save_heatmap_image(recipe, transposed_data, info_for_heatmap, True)


def create_img_for_video(recipe: VideoRecipe):

    for frame_id in range(recipe.first_frame_number, recipe.last_frame_number):
        img = get_images_by_number(recipe, frame_id)
        img2 = get_images_by_number(recipe, frame_id+1)

        remove_single_pixels_image(recipe, img)
        remove_single_pixels_image(recipe, img2)

        use_dark_frames_image(recipe, img)
        use_dark_frames_image(recipe, img2)

        correct_matrix_image(recipe, img)
        correct_matrix_image(recipe, img2)

    pass