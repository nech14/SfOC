from src.logging.errors import ErrorCode
from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.logging.logging import LOGGER


def use_dark_frames_image(recipe: BaseRecipes, img: AbstractImg) -> AbstractImg|None:
    try:
        if recipe.dark:
            LOGGER.debug(ErrorCode.START_USE_DARK_FRAMES, recipe)
            if len(recipe.dark_data) <= 0:
                recipe.get_dark_files()
            recipe.open_dark_by_datetime(img.get_datetime())
            img.dark_frames_by_recipe(recipe)
            LOGGER.debug(ErrorCode.SUCCESS_USE_DARK_FRAMES)
        return img
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_USE_DARK_FRAMES, e)


def remove_single_pixels_image(recipe: BaseRecipes, img: AbstractImg) -> AbstractImg|None:
    try:
        if recipe.remove_single_pixels:
            LOGGER.debug(ErrorCode.START_REMOVE_SINGLE_PIXELS, recipe)
            img.remove_single_pixels()
            LOGGER.debug(ErrorCode.SUCCESS_REMOVE_SINGLE_PIXELS)
        return img
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_REMOVE_SINGLE_PIXELS, e)


