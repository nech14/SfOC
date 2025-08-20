import os
from pathlib import Path

from src.file import file
from src.models.imges.img_model import Img
from src.models.recipes.base_recipes_model import BaseRecipes
from src.models.recipes.heatmap_recipe_model import HeatmapRecipe
from src.models.recipes.image_recipe_model import ImageRecipe


def get_image(recipe: ImageRecipe) -> Img:
    if recipe.files_path is None or len(recipe.files_path) == 0:
        recipe.get_path_files()
    name_path = recipe.files_path[recipe.frame_number]
    info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
    return Img(data, recipe.fit_format(info))

def get_images_path(recipe: HeatmapRecipe) -> list[Path]:
    if recipe.files_path is None or len(recipe.files_path) == 0:
        recipe.get_path_files()
    return recipe.files_path

def get_images_by_number(recipe: BaseRecipes, number: int) -> Img:
    if recipe.files_path is None or len(recipe.files_path) == 0:
        recipe.get_path_files()
    name_path = recipe.files_path[number]
    info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
    return Img(data, recipe.fit_format(info))

