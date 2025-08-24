from enum import StrEnum


class ErrorCode(StrEnum):
    # correct_matrix_image
    START_USE_CORRECT_MATRIX     = "Starting correct_matrix_image for recipe %s"
    SUCCESS_USE_CORRECT_MATRIX   = "Correction matrix applied successfully"
    ERROR_USE_CORRECT_MATRIX     = "Error in correct_matrix_image"

    # rayleigh_image
    START_RAYLEIGH_IMAGE         = "Starting rayleigh_image for recipe %s"
    SUCCESS_RAYLEIGH_IMAGE       = "Rayleigh computation finished successfully"
    ERROR_RAYLEIGH_IMAGE         = "Error in rayleigh_image"

    # auto_contrast_image
    START_AUTO_CONTRAST_IMAGE    = "Starting auto_contrast_image for recipe %s"
    SUCCESS_AUTO_CONTRAST_IMAGE  = "Auto contrast applied successfully"
    ERROR_AUTO_CONTRAST_IMAGE    = "Error in auto_contrast_image"

    # auto_contrast_result
    START_AUTO_CONTRAST_RESULT   = "Starting auto_contrast_result for recipe %s"
    SUCCESS_AUTO_CONTRAST_RESULT = "Auto contrast result computed successfully"
    ERROR_AUTO_CONTRAST_RESULT   = "Error in auto_contrast_result"

    # cut_image
    START_CUT_IMAGE   = "Starting cut_image for recipe %s"
    SUCCESS_CUT_IMAGE = "Image cutting applied successfully"
    ERROR_CUT_IMAGE   = "Error in cut_image"

    # get_image
    START_GET_IMAGE   = "Starting get_image for recipe %s"
    SUCCESS_GET_IMAGE = "Image loaded successfully"
    ERROR_GET_IMAGE   = "Error in get_image"

    # get_images_path
    START_GET_IMAGES_PATH   = "Getting images path for recipe %s"
    SUCCESS_GET_IMAGES_PATH = "Images path retrieved successfully"
    ERROR_GET_IMAGES_PATH   = "Error in get_images_path"

    # get_images_by_number
    START_GET_IMAGE_BY_NUMBER   = "Getting image #%s for recipe %s"
    SUCCESS_GET_IMAGE_BY_NUMBER = "Image #%s loaded successfully"
    ERROR_GET_IMAGE_BY_NUMBER   = "Error in get_images_by_number"

    # use_dark_frames_image
    START_USE_DARK_FRAMES = "Starting use_dark_frames_image for recipe %s"
    SUCCESS_USE_DARK_FRAMES = "Dark frames applied successfully"
    ERROR_USE_DARK_FRAMES = "Error in use_dark_frames_image"

    # remove_single_pixels_image
    START_REMOVE_SINGLE_PIXELS = "Starting remove_single_pixels_image for recipe %s"
    SUCCESS_REMOVE_SINGLE_PIXELS = "Single pixels removed successfully"
    ERROR_REMOVE_SINGLE_PIXELS = "Error in remove_single_pixels_image"

    # show_image
    START_SHOW_IMAGE = "Starting show_image for recipe %s"
    SUCCESS_SHOW_IMAGE = "Image displayed successfully"
    ERROR_SHOW_IMAGE = "Error in show_image"