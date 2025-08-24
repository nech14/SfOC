import os
from pathlib import Path

import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.models.images_models.video_img_model import VideoImg
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.models.recipes_models.image_recipe_model import ImageRecipe
from src.models.recipes_models.video_recipe_model import VideoRecipe


def save_image_by_recipe(recipe: ImageRecipe, image) -> Path:
    if not os.path.exists(recipe.save_folder):
        os.makedirs(recipe.save_folder)

    plt.title(f"{recipe.name}")
    plt.figure(figsize=recipe.figsize, dpi=100)
    plt.imshow(image, cmap="gray")
    plt.gca().invert_yaxis()
    plt.axis('off')
    if recipe.file_name is None:
        file_name_buf = recipe.files_names[recipe.frame_number]
    else:
        file_name_buf = recipe.file_name

    save_path = recipe.save_folder + f"/{file_name_buf}.png"
    save_path = Path(save_path)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    return save_path


def save_heatmap_image_by_recipe(recipe: HeatmapRecipe, image, info_for_heatmap, show=False) -> Path:
    plt.figure(figsize=recipe.figsize, dpi=100)

    if recipe.title:
        plt.title(recipe.title)

    # Создаем копию колормэпа, чтобы модифицировать
    cmap = plt.get_cmap(recipe.cmap).copy()
    if not recipe.cmap_under is None:
        cmap.set_under(recipe.cmap_under)  # значения ниже минимального будут белыми
        plt.imshow(image, cmap=cmap, aspect='auto', vmin=0.0001)
    else:
        plt.imshow(image, cmap=cmap, aspect='auto')

    colorbar = plt.colorbar()
    colorbar.set_label('n in bin')

    y_positions = np.linspace(0, image.shape[0] - 1, 10)  # Позиции меток на графике
    y_labels = np.linspace(recipe.hist_limits.xmin, recipe.hist_limits.xmax, 10)

    plt.yticks(y_positions, [int(label) for label in y_labels], fontsize=8)  # Устанавливаем метки
    plt.ylabel("y")
    plt.gca().invert_yaxis()

    plt.xlabel("time")
    plt.xticks(np.arange(0, len(info_for_heatmap), 10), info_for_heatmap[::10], rotation=45, ha='right', fontsize=8)

    name_file = recipe.file_name
    if name_file is None:
        name_file = recipe.name

    save_path = recipe.save_folder + f'/{name_file}.png'
    save_path = Path(save_path)

    if not recipe.save_folder is None:
        if not os.path.exists(recipe.save_folder):
            # Если папки не существует, создаем её
            os.makedirs(recipe.save_folder)
        plt.savefig(save_path)

    if show:
        plt.show()
    plt.close()

    return save_path


def save_image_for_video_by_recipe(recipe: VideoRecipe, duo_img: VideoImg) -> Path:
    if not os.path.exists(recipe.save_folder):
        os.makedirs(recipe.save_folder)
    img = cv2.cvtColor(duo_img.view_data, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=recipe.figsize, dpi=500)
    plt.imshow(img)
    plt.axis('off')
    # plt.savefig(save_folder + f"/{i}.png", bbox_inches='tight')
    if recipe.file_name is None:
        file_name_buf = f"{duo_img.img_first.fit_format.get_datetime()}".replace(":", "-")
    else:
        file_name_buf = recipe.file_name

    save_path = recipe.save_folder + f"/{file_name_buf}.png"
    save_path = Path(save_path)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

    return save_path