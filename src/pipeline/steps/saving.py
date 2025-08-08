import os

import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.models.imges.abstract_img import AbstractImg
from src.models.imges.duo_img_model import DuoImg
from src.models.recipes.base_recipes_model import BaseRecipes
from src.models.recipes.hearmap_recipe_model import HeatmapRecipe
from src.models.recipes.image_recipe_model import ImageRecipe
from src.models.recipes.video_recipe_model import VideoRecipe
from src.pipeline.utils.save import create_mp4

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


def save_video(recipe: VideoRecipe, frames: list[DuoImg]) -> None:
    save_folder_video = recipe.save_folder_video
    if save_folder_video is None:
        save_folder_video = recipe.name_file_video

    create_mp4(
        frames=frames,
        name=recipe.name_file_video,
        flag_info=recipe.flag_info,
        save_folder=save_folder_video,
        fps=recipe.fps,
        frames_s=1,
        logfun=recipe.logfun)