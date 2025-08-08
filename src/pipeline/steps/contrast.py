from src.models.imges.abstract_img import AbstractImg
from src.models.recipes.base_recipes_model import BaseRecipes
from src.models.recipes.hearmap_recipe_model import HeatmapRecipe
from src.pipeline.utils.graphics_helpers import auto_contrast_skimage


def auto_contrast_image(recipe: BaseRecipes, img: AbstractImg) -> list:
    if recipe.auto_contrast:
        return img.auto_contrast_version(recipe.auto_contrast_percentiles)
    return img.data

def auto_contrast_result(recipe: HeatmapRecipe, img) -> list:
    if recipe.result_auto_contrast:
        result, _, _ = auto_contrast_skimage(img, auto_contrast_percentiles=[2, 98])
        return result
    return img