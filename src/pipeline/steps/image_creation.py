import cv2

from src.logging.errors import ErrorCode
from src.models.images_models.video_img_model import VideoImg
from src.models.recipes_models.video_recipe_model import VideoRecipe
from src.utils.logics.create_image import create_img_for_video
from src.utils.logics.work_with_hist import create_hists
from main import LOGGER


def create_image_with_hist(recipe: VideoRecipe, duo_img: VideoImg, diff_last=None) -> VideoImg:
    if not recipe.hist:
        return duo_img
    try:
        LOGGER.debug(ErrorCode.START_CREATE_IMAGE_WITH_HIST, recipe)
        img = duo_img.view_data

        img_first = duo_img.img_first.data.copy()
        img_second = duo_img.img_second.data.copy()

        diff = duo_img.get_diff(recipe)
        img_hist = create_hists(img_first, img_second, diff, diff_last,
                                figsize_x=(img.shape[1] + 0.5) / 100, figsize_y=img.shape[0] / 100,
                                hist_limits=recipe.hist_limits, bins=recipe.bins)
        img_hist_BGR = cv2.cvtColor(img_hist, cv2.COLOR_RGB2BGR)
        duo_img.view_data = cv2.vconcat([img, img_hist_BGR])
        LOGGER.debug(ErrorCode.SUCCESS_CREATE_IMAGE_WITH_HIST)
        return duo_img
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_CREATE_IMAGE_WITH_HIST, e)


def create_base_img_for_video(recipe: VideoRecipe, duo_img: VideoImg) -> VideoImg:
    try:
        LOGGER.debug(ErrorCode.START_CREATE_BASE_IMG_FOR_VIDEO, recipe)
        duo_img.view_data = create_img_for_video(
            duo_img.img_first.data,
            duo_img.img_second.data,
            name=recipe.name, _type=1,
            names=[f"{duo_img.img_first.fit_format.get_datetime()}", f"{duo_img.img_second.fit_format.get_datetime()}"],
            upper_limit=500., lower_limit=None, auto_contrast=recipe.auto_contrast,
            auto_contrast_percentiles=recipe.auto_contrast_percentiles
        )
        LOGGER.debug(ErrorCode.SUCCESS_CREATE_BASE_IMG_FOR_VIDEO)
        return duo_img
    except Exception as e:
        LOGGER.exception(ErrorCode.ERROR_CREATE_BASE_IMG_FOR_VIDEO, e)

