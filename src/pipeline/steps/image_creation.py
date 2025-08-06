import cv2

from src.models.imges.duo_img_model import DuoImg
from src.models.recipes.video_recipe_model import VideoRecipe


def create_image_with_hist(recipe: VideoRecipe, duo_img: DuoImg, diff_last=None) -> DuoImg:
    if not recipe.hist:
        return duo_img

    img = duo_img.view_data

    data = duo_img.img_first.data.copy()
    data1 = duo_img.img_second.data.copy()

    diff = data - data1

    if (recipe.xmax_data is None or recipe.xmin_data is None or
        recipe.ymax_data is None or recipe.ymin_data is None):
        recipe.found_limits()

    img_hist = graphics.create_hists(data, data1, diff, diff_last, figsize_x=(img.shape[1] + 0.5) / 100,
                                     figsize_y=img.shape[0] / 100,
                                     xmin_data=recipe.xmin_data, xmax_data=recipe.xmax_data, xmin_diff=recipe.xmin_diff, xmax_diff=recipe.xmax_diff,
                                     ymin_data=recipe.ymin_data, ymax_data=recipe.ymax_data, ymin_diff=0, ymax_diff=recipe.ymax_diff,
                                     bins=recipe.bins)
    img_hist_BGR = cv2.cvtColor(img_hist, cv2.COLOR_RGB2BGR)
    duo_img.view_data = cv2.vconcat([img, img_hist_BGR])
    return duo_img

def create_base_img_for_video(recipe: VideoRecipe, duo_img: DuoImg) -> DuoImg:
    duo_img.view_data = graphics.create_img_for_video(
        duo_img.img_first.data,
        duo_img.img_second.data,
        name=recipe.name, _type=1,
        names=[f"{duo_img.img_first.fit_format.get_datetime()}", f"{duo_img.img_second.fit_format.get_datetime()}"],
        upper_limit=500., lower_limit=None, auto_contrast=recipe.auto_contrast,
        auto_contrast_percentiles=recipe.auto_contrast_percentiles
    )
    return duo_img