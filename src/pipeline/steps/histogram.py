import numpy as np
from matplotlib import pyplot as plt

from src.logging.errors import ErrorCode
from src.models.images_models.img_model import Img
from src.models.recipes_models.hist_recipe_model import HistRecipe
from src.logging.logging import LOGGER


def create_hist(recipe: HistRecipe, img: Img) -> np.ndarray|None:
    try:
        LOGGER.debug(ErrorCode.START_CREATE_HIST, recipe)
        bins = np.linspace(0, recipe.hist_limits.xmax, recipe.bins)
        result_hist, _, _ = plt.hist(img.data.flatten(), bins=bins)
        plt.close()
        LOGGER.debug(ErrorCode.SUCCESS_CREATE_HIST)
        return result_hist
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_CREATE_HIST, e)

    # hist, _, _ =  create_hists(
    #     img.data, bins=bins,
    #     hist_limits=recipe.hist_limits,
    #     return_data=True, show=True)
    # return hist



