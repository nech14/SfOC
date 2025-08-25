from src.logging.errors import ErrorCode
from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.logging.logging import LOGGER


def show_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    try:
        if recipe.show:
            LOGGER.debug(ErrorCode.START_SHOW_IMAGE, recipe)
            img.show(recipe)
            LOGGER.debug(ErrorCode.SUCCESS_SHOW_IMAGE)
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_SHOW_IMAGE, e)





