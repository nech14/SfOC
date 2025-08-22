import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.models.images_models.duo_img_model import DuoImg
from src.models.recipes_models.video_recipe_model import VideoRecipe
from src.pipeline.utils.helpers import drive_to_color_palette, create_hists
from src.pipeline.utils.graphics_helpers import auto_contrast_skimage
from src.pipeline.utils.save import save_heat_map


def create_image_with_hist(recipe: VideoRecipe, duo_img: DuoImg, diff_last=None) -> DuoImg:
    if not recipe.hist:
        return duo_img

    img = duo_img.view_data

    img_first = duo_img.img_first.data.copy()
    img_second = duo_img.img_second.data.copy()

    diff = img_first - img_second

    if (recipe.xmax_data is None or recipe.xmin_data is None or
        recipe.ymax_data is None or recipe.ymin_data is None):
        recipe.found_limits()

    img_hist = create_hists(img_first, img_second, diff, diff_last,
                            figsize_x=(img.shape[1] + 0.5) / 100, figsize_y=img.shape[0] / 100,
                            xmin_data=recipe.xmin_data, xmax_data=recipe.xmax_data,
                            xmin_diff=recipe.xmin_diff, xmax_diff=recipe.xmax_diff,
                            ymin_data=recipe.ymin_data, ymax_data=recipe.ymax_data,
                            ymin_diff=0, ymax_diff=recipe.ymax_diff,
                            bins=recipe.bins)
    img_hist_BGR = cv2.cvtColor(img_hist, cv2.COLOR_RGB2BGR)
    duo_img.view_data = cv2.vconcat([img, img_hist_BGR])
    return duo_img

def create_base_img_for_video(recipe: VideoRecipe, duo_img: DuoImg) -> DuoImg:
    duo_img.view_data = create_img_for_video(
        duo_img.img_first.data,
        duo_img.img_second.data,
        name=recipe.name, _type=1,
        names=[f"{duo_img.img_first.fit_format.get_datetime()}", f"{duo_img.img_second.fit_format.get_datetime()}"],
        upper_limit=500., lower_limit=None, auto_contrast=recipe.auto_contrast,
        auto_contrast_percentiles=recipe.auto_contrast_percentiles
    )
    return duo_img



def create_img_for_video(
        data, data1, name=None, names=None, text_place="t", _type=1, upper_limit=500.,
        lower_limit=None, auto_contrast=True, auto_contrast_percentiles=[2, 98]
):
    ulimit = 10000
    dlimit = 5000
    ulimit_diff = 900
    dlimit_diff = 0
    cmap = plt.get_cmap('gray')

    combined_image = cv2.hconcat([ cv2.resize(data,(512, 512)), cv2.resize(data1,(512, 512))])

    if auto_contrast:
        processed_image, _, _ = auto_contrast_skimage(combined_image, auto_contrast_percentiles=auto_contrast_percentiles)
    else:
        processed_image = combined_image
    cmap_image = np.array(processed_image)

    cmap_image_max = np.max(cmap_image[~np.isnan(cmap_image)])

    cmap_image = drive_to_color_palette(cmap_image, 0, cmap_image_max, cmap)

    if _type == 0: #Gray
        diff = cv2.absdiff(data, data1)

        diff_cmap = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)
        diff_cmap = cv2.cvtColor(diff_cmap, cv2.COLOR_RGB2BGR)
        cmap_image = cv2.cvtColor(cmap_image, cv2.COLOR_GRAY2BGR)


    elif _type == 1: #heat map
        diff = data - data1
        diff_cmap = save_heat_map(diff, upper_limit=upper_limit, lower_limit=lower_limit)
        diff_cmap = cv2.cvtColor(diff_cmap, cv2.COLOR_RGB2BGR)
        cmap_image = cv2.cvtColor(cmap_image, cv2.COLOR_GRAY2BGR)


    elif _type == 2: #abs heat map
        # diff = data.astype(float) - data1.astype(float)
        diff = data - data1

        diff_cmap = drive_to_color_palette(diff, dlimit_diff, ulimit_diff, cmap)

        diff_cmap = cv2.cvtColor(diff_cmap, cv2.COLOR_RGB2BGR)
        cmap_image = cv2.cvtColor(cmap_image, cv2.COLOR_GRAY2BGR)

    else:
        return

    if names:
        top_border = 50
        bottom_border = 50
        left_border = 0
        right_border = 0

        expanded_image = cv2.copyMakeBorder(cmap_image, top_border, bottom_border, left_border, right_border,
                                            cv2.BORDER_CONSTANT)
        expanded_image_diff = cv2.copyMakeBorder(diff_cmap, top_border, bottom_border, left_border, right_border,
                                                 cv2.BORDER_CONSTANT)

        n = data.shape[1] // 14
        text = names[0] + ' ' * n + " " + ' ' * n + names[1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        font_thickness = 1
        text_color = (255, 255, 255)

        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

        if text_place == 'b':
            text_position = ((expanded_image.shape[1] - text_size[0]) // 2, cmap_image.shape[0] + top_border + 30)
        elif text_place == 't':
            text_position = ((expanded_image.shape[1] - text_size[0]) // 2, top_border - 10)
        else:
            text_position = ((expanded_image.shape[1] - text_size[0]) // 2, cmap_image.shape[0] + top_border + 30)

        cv2.putText(expanded_image, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        cv2.putText(expanded_image_diff, "    diff", text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)


        mistake = expanded_image_diff.shape[0] - expanded_image.shape[0]
        result = cv2.hconcat([expanded_image, expanded_image_diff[mistake:]])
    else:
        result = cv2.hconcat([cmap_image, diff_cmap])

    if name:
        top_border = 50
        bottom_border = 0
        left_border = 0
        right_border = 0

        # Расширение изображения
        expanded_image = cv2.copyMakeBorder(result, top_border, bottom_border, left_border, right_border,
                                            cv2.BORDER_CONSTANT)

        # Добавление текста
        text = name
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 1
        text_color = (255, 255, 255)  # Цвет текста в формате BGR

        # Определение размера текста для вычисления координат центра
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

        # Определение координат текста в расширенной области
        text_position = ((expanded_image.shape[1] - text_size[0]) // 2, top_border - 10)

        # Нанесение текста на изображение
        cv2.putText(expanded_image, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        return expanded_image

    return result