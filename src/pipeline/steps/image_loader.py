import os

from src.file import file
from src.models.imges.img_model import Img
from src.models.recipes.base_recipes_model import BaseRecipes
from src.models.recipes.hearmap_recipe_model import HeatmapRecipe
from src.models.recipes.image_recipe_model import ImageRecipe


def get_image(recipe: ImageRecipe) -> Img:
    if recipe.names_files is None or len(recipe.names_files) == 0:
        recipe.get_names_files()
    name_path = os.path.join(recipe.root_path, recipe.names_files[recipe.frame_number])
    info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
    return Img(data, recipe.fit_format(info))

def get_images_path(recipe: HeatmapRecipe) -> list[str]:
    if recipe.names_files is None or len(recipe.names_files) == 0:
        recipe.get_names_files()
    return recipe.names_files

def get_images_by_number(recipe: BaseRecipes, number: int) -> Img:
    if recipe.names_files is None or len(recipe.names_files) == 0:
        recipe.get_names_files()
    name_path = os.path.join(recipe.root_path, recipe.names_files[number])
    info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
    return Img(data, recipe.fit_format(info))

