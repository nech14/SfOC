import os
from pathlib import Path
from src.logging.errors import ErrorCode
from src.models.images_models.abstract_img import AbstractImg
from src.models.images_models.video_img_model import VideoImg
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.models.recipes_models.image_recipe_model import ImageRecipe
from src.models.recipes_models.video_recipe_model import VideoRecipe
from src.pipeline.utils.save import create_mp4
from src.utils.logics.save_logic import save_image_by_recipe, save_heatmap_image_by_recipe, \
    save_image_for_video_by_recipe
from src.logging.logging import LOGGER


def save_result_matrix_image(recipe: BaseRecipes, img: AbstractImg) -> Path | None:
    if not recipe.result_matrix_save_folder:
        return None
    try:
        LOGGER.debug(ErrorCode.START_SAVE_RESULT_MATRIX_IMAGE, recipe)
        if recipe.save_folder:
            recipe.result_matrix_safe_folder = os.path.join(recipe.save_folder, "result_matrix")
        path = img.save_rayleigh_matrix(folder=recipe.result_matrix_safe_folder, filename=recipe.file_name)
        LOGGER.debug(ErrorCode.SUCCESS_SAVE_RESULT_MATRIX_IMAGE)
        return path
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_SAVE_RESULT_MATRIX_IMAGE, e)


def save_image(recipe: ImageRecipe, image) -> Path|None:
    if not recipe.save_folder:
        return None
    try:
        LOGGER.debug(ErrorCode.START_SAVE_IMAGE, recipe)
        result = save_image_by_recipe(recipe, image)
        LOGGER.debug(ErrorCode.SUCCESS_SAVE_IMAGE)
        return result
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_SAVE_IMAGE, e)


def save_heatmap_image(recipe: HeatmapRecipe, image, info_for_heatmap, show=False) -> Path|None:
    if not recipe.save_folder:
        return None
    try:
        LOGGER.debug(ErrorCode.START_SAVE_HEATMAP_IMAGE, recipe)
        result = save_heatmap_image_by_recipe(recipe, image, info_for_heatmap, show)
        LOGGER.debug(ErrorCode.SUCCESS_SAVE_HEATMAP_IMAGE)
        return result
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_SAVE_HEATMAP_IMAGE, e)


def save_image_for_video(recipe: VideoRecipe, duo_img: VideoImg) -> Path|None:
    if not recipe.save_folder:
        return None
    try:
        LOGGER.debug(ErrorCode.START_SAVE_IMAGE_FOR_VIDEO, recipe)
        result = save_image_for_video_by_recipe(recipe, duo_img)
        LOGGER.debug(ErrorCode.SUCCESS_SAVE_IMAGE_FOR_VIDEO)
        return result
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_SAVE_IMAGE_FOR_VIDEO, e)


def save_video(recipe: VideoRecipe, frames: list[VideoImg]) -> Path|None:
    try:
        LOGGER.debug(ErrorCode.START_SAVE_VIDEO, recipe)
        save_folder_video = recipe.save_folder_video
        if save_folder_video is None:
            save_folder_video = recipe.name_file_video
        result = create_mp4(
            frames=frames,
            name=recipe.name_file_video,
            flag_info=recipe.flag_info,
            save_folder=save_folder_video,
            fps=recipe.fps,
            frames_s=1,
            logfun=recipe.logfun)
        LOGGER.debug(ErrorCode.SUCCESS_SAVE_VIDEO)
        return result
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_SAVE_VIDEO, e)