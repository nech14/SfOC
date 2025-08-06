from src.models.imges.abstract_img import AbstractImg
from src.models.recipes.base_recipes_model import BaseRecipes


def correct_matrix_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if not recipe.correct_matrix_path is None:
        if recipe.correct_matrix is None:
            recipe.open_correct_matrix()
        img.correct_matrix(recipe.correct_matrix, recipe.multiplication_on_correct_matrix)

def rayleigh_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.rayleigh:
        img.rayleigh()
