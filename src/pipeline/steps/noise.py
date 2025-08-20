import matplotlib.pyplot as plt

from src.models.imges.abstract_img import AbstractImg
from src.models.recipes.base_recipes_model import BaseRecipes


def use_dark_frames_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.dark:
        # if recipe.dark_start is None or recipe.dark_start is None:
        #     recipe.open_dark()
        if len(recipe.dark_data) <= 0:
            recipe.get_dark_files()

        # if recipe.dark_start is None a recipe.dark_start is None:
        recipe.open_dark_by_datetime(img.fit_format.get_datetime())

        # plt.subplot(121)
        # plt.imshow(recipe.dark_start.frame)
        # plt.subplot(122)
        # plt.imshow(recipe.dart_end.frame)
        # plt.show()

        img.dark_frames(recipe.dark_start, recipe.dart_end)


def remove_single_pixels_image(recipe: BaseRecipes, img: AbstractImg) -> None:
    if recipe.remove_single_pixels:
        img.remove_single_pixels()


