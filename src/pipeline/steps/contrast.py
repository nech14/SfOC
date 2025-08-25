from src.logging.errors import ErrorCode
from src.models.images_models.abstract_img import AbstractImg
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.pipeline.utils.graphics_helpers import auto_contrast_skimage
from src.logging.logging import LOGGER


def auto_contrast_image(recipe: BaseRecipes, img: AbstractImg) -> list:
    try:
        if recipe.auto_contrast:
            LOGGER.debug(ErrorCode.START_AUTO_CONTRAST_IMAGE, recipe)
            img.auto_contrast_version(recipe.auto_contrast_percentiles)
            LOGGER.debug(ErrorCode.SUCCESS_AUTO_CONTRAST_IMAGE)
        return img.view_data
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_AUTO_CONTRAST_IMAGE, e)


def auto_contrast_result(recipe: HeatmapRecipe, img) -> list:
    try:
        if recipe.result_auto_contrast:
            LOGGER.debug(ErrorCode.START_AUTO_CONTRAST_RESULT, recipe)
            result, _, _ = auto_contrast_skimage(img, auto_contrast_percentiles=[2, 98])
            LOGGER.debug(ErrorCode.SUCCESS_AUTO_CONTRAST_RESULT)
            return result
        return img
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_AUTO_CONTRAST_RESULT, e)