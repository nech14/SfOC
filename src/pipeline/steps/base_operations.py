from src.models.imges.abstract_img import AbstractImg
from src.models.recipes.base_recipes_model import BaseRecipes
from src.pipeline.steps.contrast import auto_contrast_image
from src.pipeline.steps.geometry import cut_image
from src.pipeline.steps.matrix_correction import correct_matrix_image, rayleigh_image
from src.pipeline.steps.noise import remove_single_pixels_image, use_dark_frames_image
from src.pipeline.steps.saving import save_result_matrix_image


def base_operation_with_img(recipe: BaseRecipes, img: AbstractImg) -> AbstractImg:
    remove_single_pixels_image(recipe, img)
    use_dark_frames_image(recipe, img)
    correct_matrix_image(recipe, img)
    rayleigh_image(recipe, img)
    cut_image(recipe, img)
    save_result_matrix_image(recipe, img)
    auto_contrast_image(recipe, img)
    return img