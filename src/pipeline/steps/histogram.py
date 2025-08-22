import numpy as np

from src.models.images_models.img_model import Img
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.pipeline.utils.helpers import create_hists


def create_hist(recipe: HeatmapRecipe, img: Img) -> np.ndarray:
    bins = np.linspace(0, recipe.hist_limits.xmax, recipe.bins)
    hist, _, _ =  create_hists(
        img.view_data, img.view_data, img.view_data, bins=bins,
        return_data=True, show=False)
    return hist


