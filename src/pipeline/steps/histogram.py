import numpy as np

from src.pipeline.utils.helpers import create_hists
from src.models.imges.img_model import Img
from src.models.recipes.heatmap_recipe_model import HeatmapRecipe


def create_hist(recipe: HeatmapRecipe, img: Img) -> np.ndarray:
    bins = np.linspace(0, recipe.hist_limits.xmax, recipe.bins)
    hist, _, _ =  create_hists(
        img.view_data, img.view_data, img.view_data, bins=bins,
        return_data=True, show=False)
    return hist


