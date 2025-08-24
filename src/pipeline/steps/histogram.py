import numpy as np
from matplotlib import pyplot as plt

from src.models.images_models.img_model import Img
from src.models.recipes_models.hist_recipe_model import HistRecipe
from src.utils.logics.work_with_hist import create_hists


def create_hist(recipe: HistRecipe, img: Img) -> np.ndarray:
    # print(f"max: {recipe.hist_limits.xmax}")
    bins = np.linspace(0, recipe.hist_limits.xmax, recipe.bins)
    result_hist, _, _ = plt.hist(img.data.flatten(), bins=bins)
    # plt.show()
    plt.close()
    # hist, _, _ =  create_hists(
    #     img.data, bins=bins,
    #     hist_limits=recipe.hist_limits,
    #     return_data=True, show=True)
    # return hist
    return result_hist


