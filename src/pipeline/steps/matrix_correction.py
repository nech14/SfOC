
from src.logging.logging import get_logger
from src.models.imges.abstract_img import AbstractImg
from src.models.recipes.base_recipes_model import BaseRecipes

logger = get_logger()

def correct_matrix_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    logger.debug("Запуск correct_matrix_image для рецепта %s", recipe)
    try:
        if not recipe.correct_matrix_path is None:
            if recipe.correct_matrix is None:
                recipe.open_correct_matrix()
            img.correct_matrix(recipe.correct_matrix, recipe.multiplication_on_correct_matrix)
    except Exception as e:
        logger.exception("Ошибка в correct_matrix_image: %s", e)
    else:
        logger.debug("Матрица коррекции успешно применена")


def rayleigh_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    logger.debug("Запуск rayleigh_image для рецепта %s", recipe)
    try:
        if recipe.rayleigh:
            img.rayleigh()
    except Exception as e:
        logger.exception("Ошибка в rayleigh_image: %s", e)
    else:
        logger.debug("Рэле посчитаны успешно")
