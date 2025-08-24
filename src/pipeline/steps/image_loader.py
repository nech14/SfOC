from pathlib import Path

from src.logging.errors import ErrorCode
from src.models.images_models.img_model import Img
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.models.recipes_models.image_recipe_model import ImageRecipe
from src.utils.file import file
from main import LOGGER


def get_image(recipe: ImageRecipe) -> Img:
    try:
        LOGGER.debug(ErrorCode.START_GET_IMAGE, recipe)
        if recipe.files_path is None or len(recipe.files_path) == 0:
            recipe.get_path_files()
        name_path = recipe.files_path[recipe.frame_number]
        info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
        LOGGER.debug(ErrorCode.SUCCESS_GET_IMAGE)
        return Img(data, recipe.fit_format(info))
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_GET_IMAGE, e)


def get_images_path(recipe: HeatmapRecipe) -> list[Path]:
    try:
        LOGGER.debug(ErrorCode.START_GET_IMAGES_PATH, recipe)
        if recipe.files_path is None or len(recipe.files_path) == 0:
            recipe.get_path_files()
        LOGGER.debug(ErrorCode.SUCCESS_GET_IMAGES_PATH)
        return recipe.files_path
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_GET_IMAGES_PATH, e)


def get_images_by_number(recipe: BaseRecipes, number: int) -> Img:
    try:
        LOGGER.debug(ErrorCode.START_GET_IMAGE_BY_NUMBER, recipe)
        if recipe.files_path is None or len(recipe.files_path) == 0:
            recipe.get_path_files()
        name_path = recipe.files_path[number]
        info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
        LOGGER.debug(ErrorCode.SUCCESS_GET_IMAGE_BY_NUMBER)
        return Img(data, recipe.fit_format(info))
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_GET_IMAGE_BY_NUMBER, e)