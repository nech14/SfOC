from pathlib import Path
from typing import TypeVar
import numpy as np
from src.models.common_models.hist_limits import HistLimits
from src.models.images_models.abstract_img import AbstractImg
from src.models.images_models.video_img_model import VideoImg
from src.models.images_models.img_model import Img
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.models.recipes_models.hist_recipe_model import HistRecipe
from src.models.recipes_models.image_recipe_model import ImageRecipe
from src.models.recipes_models.video_recipe_model import VideoRecipe
from src.pipeline.base_pipelines.base_operations import base_operation_with_img
from src.pipeline.steps.contrast import auto_contrast_result
from src.pipeline.steps.histogram import create_hist
from src.pipeline.steps.image_creation import create_base_img_for_video, create_image_with_hist
from src.pipeline.steps.image_loader import get_image, get_images_by_number
from src.pipeline.steps.saving import save_image, save_heatmap_image, save_image_for_video, \
    save_video
from src.pipeline.steps.show_data import show_image
from src.utils.logics.work_with_hist import get_hist_parameters, get_hist_parameters_images

T = TypeVar("T", bound=AbstractImg)

def create_image(recipe: ImageRecipe) -> AbstractImg:
    img = get_image(recipe)
    img = base_operation_with_img(recipe, img)
    save_image(recipe, img.view_data)
    # plt.imshow(img.view_data, cmap="gray")
    # plt.gca().invert_yaxis()
    # plt.show()
    return img


def _get_hist_found_limits_with_one_image(recipe: HistRecipe, img: T) -> T:
    base_operation_with_img(recipe, img)
    return img


def get_hist_found_limits(recipe: HistRecipe) -> HistLimits:
    if not recipe.hist_limits is None: return recipe.hist_limits

    hist_limits = HistLimits()
    check_frame = recipe.get_check_frame()

    for frame_id in check_frame:
        img = get_images_by_number(recipe, frame_id)

        img = _get_hist_found_limits_with_one_image(recipe, img)

        limits = get_hist_parameters(img, recipe.bins)
        hist_limits.add_base_limits(*limits)
    return hist_limits


def get_hist_found_limits_images(recipe: HistRecipe) -> HistLimits:
    if not recipe.hist_limits is None: return recipe.hist_limits

    hist_limits = HistLimits()
    check_frame = recipe.get_check_frame()

    for frame_id in check_frame:
        img_first = get_images_by_number(recipe, frame_id)
        img_second = get_images_by_number(recipe, frame_id+1)
        duo_img = VideoImg(img_first, img_second)

        duo_img: VideoImg = _get_hist_found_limits_with_one_image(recipe, duo_img)
        diff = duo_img.get_diff(recipe)

        limits = get_hist_parameters_images(img_first, img_second, diff=diff,bins=recipe.bins)
        hist_limits.add_limits(*limits)
    return hist_limits


def _create_column_for_heatmap(recipe: HeatmapRecipe, img: Img) -> np.ndarray:
    _get_hist_found_limits_with_one_image(recipe, img)
    hist = create_hist(recipe, img)
    return hist


def create_heatmap(recipe: HeatmapRecipe) -> None:
    data_for_heatmap = []
    info_for_heatmap = []

    recipe.hist_limits = get_hist_found_limits(recipe)
    print(f"first_frame_number: {recipe.first_frame_number, recipe.last_frame_number}")
    for frame_id in range(recipe.first_frame_number, recipe.last_frame_number):
        print(f"hist_frame: {frame_id}")
        img = get_images_by_number(recipe, frame_id)

        # img.show(recipe)

        hist = _create_column_for_heatmap(recipe, img)
        data_for_heatmap.append(hist)
        info_for_heatmap.append(img.fit_format.get_datetime().time())

    data_for_heatmap = np.array(data_for_heatmap)
    transposed_data = np.transpose(data_for_heatmap)
    transposed_data = auto_contrast_result(recipe, transposed_data)
    save_heatmap_image(recipe, transposed_data, info_for_heatmap, False)


def create_image_for_video(recipe: VideoRecipe, frame_number:int, last_diff: list | None = None) -> VideoImg:
    img1 = get_images_by_number(recipe, frame_number)
    img2 = get_images_by_number(recipe, frame_number + 1)
    duo_img = VideoImg(img1, img2)

    base_operation_with_img(recipe, duo_img)
    create_base_img_for_video(recipe, duo_img)
    create_image_with_hist(recipe, duo_img, last_diff)
    show_image(recipe, duo_img)
    save_image_for_video(recipe, duo_img)
    return duo_img


def create_images_for_video(recipe: VideoRecipe) -> list[VideoImg]:
    frames: list[VideoImg] = []
    last_diff = None
    recipe.hist_limits = get_hist_found_limits_images(recipe)
    for frame_id in range(recipe.first_frame_number, recipe.last_frame_number):
        print(f"create: {frame_id}")
        img = create_image_for_video(recipe, frame_id, last_diff)
        frames.append(img)
        last_diff=frames[-1].get_diff(recipe)

    return frames


def create_video(recipe: VideoRecipe) -> Path:
    images = create_images_for_video(recipe)
    frames = [i.view_data for i in images]
    return save_video(recipe, frames)
