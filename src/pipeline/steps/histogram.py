import numpy as np

from src.models.imges.img_model import Img
from src.models.recipes.hearmap_recipe_model import HeatmapRecipe


def create_hist(recipe: HeatmapRecipe, img: Img):
    if recipe.xmax_data is None or recipe.xmin_data is None:
        recipe.found_limits()

    # bins = range(0, 10000, 100)
    # bins = np.linspace(recipe.xmin_data, recipe.xmax_data, recipe.bins-2)
    bins = np.linspace(0, recipe.xmax_data, recipe.bins)
    # bins = np.insert(bins, 0 ,0)
    # bins = np.append(bins, 800000)


    hist, _, _ = graphics.create_hists(
        img.data, img.data, img.data, bins=bins,
        return_data=True, show=False)

    return hist