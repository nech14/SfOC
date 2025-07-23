import os
import pickle

import matplotlib.pyplot as plt

from src import file
from src.models.image_recipe_model import ImageRecipe
from src.models.img_model import Img


def get_image(recipe: ImageRecipe) -> Img:
    if recipe.names_files is None or len(recipe.names_files) == 0:
        recipe.get_names_files()
    name_path = os.path.join(recipe.root_path, recipe.names_files[recipe.frame_number])
    info, data = file.open_gz(name_path, _zip=recipe.zipped_file)
    return Img(data, recipe.fit_format(info))

def use_dark_frames_image(recipe: ImageRecipe, img: Img) -> None:
    if recipe.dark:
        if recipe.dark_start is None or recipe.dark_start is None:
            recipe.open_dark()
        img.dark_frames(recipe.dark_start, recipe.dart_end)

def remove_single_pixels_image(recipe: ImageRecipe, img: Img) -> None:
    if recipe.remove_single_pixels:
        img.remove_single_pixels()

def correct_matrix_image(recipe: ImageRecipe, img: Img) -> None:
    if not recipe.correct_matrix_path is None:
        if recipe.correct_matrix is None:
            recipe.open_correct_matrix()
        img.correct_matrix(recipe.correct_matrix, recipe.multiplication_on_correct_matrix)

def rayleigh_image(recipe: ImageRecipe, img: Img) -> None:
    if recipe.rayleigh:
        img.rayleigh()

def cut_image(recipe: ImageRecipe, img: Img) -> None:
    if recipe.cut:
        img.cut(percent_to_trim=recipe.percent_to_trim)

def auto_contrast_image(recipe: ImageRecipe, img: Img) -> list:
    if recipe.auto_contrast:
        return img.auto_contrast_version(recipe.auto_contrast_percentiles)
    return img.data

def save_result_matrix_image(recipe: ImageRecipe, img: Img) -> None:
    if recipe.result_matrix_save_folder is None:
        return

    if recipe.result_matrix_save_folder == "" and not recipe.save_folder is None and recipe.save_folder != "":
        recipe.result_matrix_safe_folder = os.path.join(recipe.save_folder, "result_matrix")

    if not os.path.exists(recipe.result_matrix_save_folder):
        os.makedirs(recipe.result_matrix_save_folder)

    result_matrix_safe_folder_data = (
        os.path.join(
            recipe.result_matrix_save_folder, f"{recipe.names_files[recipe.frame_number]}.pkl"
        )
    )

    with open(result_matrix_safe_folder_data, 'wb') as file:
        pickle.dump(img.data, file)


def save_image(recipe: ImageRecipe, processed_image) -> None:
    if not os.path.exists(recipe.save_folder):
        # Если папки не существует, создаем её
        os.makedirs(recipe.save_folder)

    plt.title(f"{recipe.name}")

    plt.figure(figsize=recipe.figsize, dpi=100)
    plt.imshow(processed_image, cmap="gray")
    plt.gca().invert_yaxis()
    plt.axis('off')
    if recipe.file_name is None:
        file_name_buf = recipe.names_files[recipe.frame_number]
    else:
        file_name_buf = recipe.file_name
    plt.savefig(recipe.save_folder + f"/{file_name_buf}.png", bbox_inches='tight')
    plt.close()


def create_image(recipe: ImageRecipe) -> None:
    img = get_image(recipe)

    remove_single_pixels_image(recipe, img)
    use_dark_frames_image(recipe, img)
    correct_matrix_image(recipe, img)
    rayleigh_image(recipe, img)
    cut_image(recipe, img)

    save_result_matrix_image(recipe, img)

    print_img = auto_contrast_image(recipe, img)
    save_image(recipe, print_img)
    plt.imshow(print_img, cmap="gray")
    plt.gca().invert_yaxis()
    plt.show()
