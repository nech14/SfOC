import matplotlib.pyplot as plt

from src.logging.logging import get_logger
from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes

logger = get_logger()

def correct_matrix_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    try:
        if recipe.use_correct_matrix:
            logger.debug("Запуск correct_matrix_image для рецепта %s", recipe)
            if recipe.correct_matrix is None:
                recipe.open_correct_matrix()
            img.correct_matrix(recipe.correct_matrix, recipe.multiplication_on_correct_matrix)
            logger.debug("Матрица коррекции успешно применена")
    except Exception as e:
        logger.exception("Ошибка в correct_matrix_image: %s", e)



def rayleigh_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    try:
        if recipe.rayleigh:
            logger.debug("Запуск rayleigh_image для рецепта %s", recipe)
            img.rayleigh()
            logger.debug("Рэле посчитаны успешно")
    except Exception as e:
        logger.exception("Ошибка в rayleigh_image: %s", e)
