from src.models.imges.abstract_img import AbstractImg
from src.models.recipes.base_recipes_model import BaseRecipes


def show_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.show:
        img.show(recipe)





