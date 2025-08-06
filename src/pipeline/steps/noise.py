from src.models.imges.abstract_img import AbstractImg
from src.models.recipes.base_recipes_model import BaseRecipes


def use_dark_frames_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.dark:
        if recipe.dark_start is None or recipe.dark_start is None:
            recipe.open_dark()
        img.dark_frames(recipe.dark_start, recipe.dart_end)


def remove_single_pixels_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.remove_single_pixels:
        img.remove_single_pixels()


