from src.logging.errors import ErrorCode
from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.logging.logging import LOGGER


def cut_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    try:
        if recipe.cut:
            LOGGER.debug(ErrorCode.START_CUT_IMAGE, recipe)
            img.cut(percent_to_trim=recipe.percent_to_trim)
            LOGGER.debug(ErrorCode.SUCCESS_CUT_IMAGE)
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_CUT_IMAGE, e)