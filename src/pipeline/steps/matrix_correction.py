from src.logging.errors import ErrorCode
from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.logging.logging import LOGGER


def correct_matrix_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    try:
        if recipe.use_correct_matrix:
            LOGGER.debug(ErrorCode.START_USE_CORRECT_MATRIX, recipe)
            if recipe.correct_matrix is None:
                recipe.open_correct_matrix()
            img.correct_matrix(recipe.correct_matrix, recipe.multiplication_on_correct_matrix)
            LOGGER.debug(ErrorCode.SUCCESS_USE_CORRECT_MATRIX)
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_USE_CORRECT_MATRIX, e)


def rayleigh_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    try:
        if recipe.rayleigh:
            LOGGER.debug(ErrorCode.START_RAYLEIGH_IMAGE, recipe)
            img.rayleigh()
            LOGGER.debug(ErrorCode.SUCCESS_RAYLEIGH_IMAGE)
        else:
            img.no_rayleigh()
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_RAYLEIGH_IMAGE, e)
