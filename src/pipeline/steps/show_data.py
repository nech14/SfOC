from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes


def show_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.show:
        img.show(recipe)





