import numpy as np
from matplotlib import pyplot as plt

from src.logics import logicks
from src.models.imges.duo_img_model import DuoImg
from src.models.imges.img_model import Img
from src.models.recipes.hearmap_recipe_model import HeatmapRecipe
from src.models.recipes.image_recipe_model import ImageRecipe
from src.models.recipes.video_recipe_model import VideoRecipe
from src.pipeline.steps.contrast import auto_contrast_image, auto_contrast_result
from src.pipeline.steps.geometry import cut_image
from src.pipeline.steps.histogram import create_hist
from src.pipeline.steps.image_creation import create_base_img_for_video, create_image_with_hist
from src.pipeline.steps.image_loader import get_image, get_images_by_number
from src.pipeline.steps.matrix_correction import correct_matrix_image, rayleigh_image
from src.pipeline.steps.noise import remove_single_pixels_image, use_dark_frames_image
from src.pipeline.steps.saving import save_result_matrix_image, save_image, save_heatmap_image, save_image_for_video
from src.pipeline.steps.show_data import show_image


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


def create_image_for_video(recipe: VideoRecipe, frame_number:int, last_diff: list | None = None) -> DuoImg:
    img1 = get_images_by_number(recipe, frame_number)
    img2 = get_images_by_number(recipe, frame_number + 1)

    duo_img = DuoImg(img1, img2)

    remove_single_pixels_image(recipe, duo_img)
    use_dark_frames_image(recipe, duo_img)
    correct_matrix_image(recipe, duo_img)
    rayleigh_image(recipe, duo_img)
    cut_image(recipe, duo_img)
    create_base_img_for_video(recipe, duo_img)
    create_image_with_hist(recipe, duo_img, last_diff)
    show_image(recipe, duo_img)
    save_image_for_video(recipe, duo_img)

    return duo_img

def create_images_for_video(recipe: VideoRecipe) -> list[DuoImg]:
    frames: list[DuoImg] = []
    last_diff = None
    for frame_id in range(recipe.first_frame_number, recipe.last_frame_number):
        img = create_image_for_video(recipe, frame_id, last_diff)
        frames.append(img)
        last_diff=frames[-1].get_diff()

    return frames

def create_video(recipe: VideoRecipe) -> None:
    images = create_images_for_video(recipe)
    frames = [i.view_data for i in images]

    save_folder_video = recipe.save_folder_video
    if save_folder_video is None:
        save_folder_video = recipe.name_file_video

    logicks.create_mp4(
        dates=frames,
        name=recipe.name_file_video,
        flag_info=recipe.flag_info,
        save_folder=save_folder_video,
        fps=recipe.fps,
        frames_s=1,
        logfun=recipe.logfun)
