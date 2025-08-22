from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes


def cut_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.cut:
        img.cut(percent_to_trim=recipe.percent_to_trim)