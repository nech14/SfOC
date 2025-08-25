import os
from pathlib import Path

from sqlalchemy import text

from src.api.requests.edit_db_request.create_heatmap_db_request import CreateHeatmapDbInternal, CreateHeatmapDbRequest
from src.api.requests.edit_db_request.create_image_db_request import CreateImageDbRequest, CreateImageDbInternal
from src.api.requests.edit_db_request.create_image_for_video_db_request import CreateImageForVideoDbInternal, \
    CreateImageForVideoDbRequest
from src.api.requests.edit_db_request.create_video_db_request import CreateVideoDbInternal, CreateVideoDbRequest
from src.api.requests.edit_db_request.get_dark_files_db_request import GetDarkFilesDbRequest
from src.database.database import Session
from src.database.models.models import BackgroundsAll, Frames
from src.models.api_models.filter_edit_db_model import FilterEditDbModel
from src.models.api_models.frame_edit_db_model import FrameEditDbModel
from src.models.recipes_models.heatmap_recipe_model import HeatmapRecipe
from src.models.recipes_models.image_recipe_model import ImageRecipe
from src.models.recipes_models.video_recipe_model import VideoRecipe
from src.pipeline import orchestrator
from src.utils.common.common import print_vars
from src.utils.common.fits_formats import fits_formats
from src.utils.logics.work_with_dark import get_dark_by_path, show_darks_frames


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def get_frame_by_id(frame_id: int) -> FrameEditDbModel:
    db = Session()
    try:
        query = text("""
            SELECT 
                frames.id as frameId, 
                frames.id_night as id_night,
                frames.dest as framePath, 
                camera.name as camera, 
                filters.name as filter, 
                paths.ucf as matrixFolder, 
                filters.ucf as matrixName
            FROM frames
            INNER JOIN filters ON frames.id_filtr = filters.id
            INNER JOIN camera ON filters.id_camera = camera.id
            INNER JOIN paths ON filters.id_camera = paths.id_camera
            WHERE frames.id = :frame_id
        """)
        result = db.execute(query, {"frame_id": frame_id}).mappings().all()
        return result[0] if result else None
    finally:
        db.close()


def get_filter_matrix_by_id(filter_id: int) -> FilterEditDbModel:
    db = Session()
    try:
        query = text("""
            SELECT 
                filters.id,
                paths.ucf as "path",
                filters.ucf as "filename" 
            FROM filters 
            INNER JOIN paths ON paths.id_camera = filters.id_camera 
            WHERE filters.id = :filter_id;
        """)
        result = db.execute(query, {"filter_id": filter_id}).mappings().all()
        return result[0] if result else None
    finally:
        db.close()


def get_dark_frames(id_night: int) -> list[BackgroundsAll]:
    db = Session()
    try:
        return db.query(BackgroundsAll).filter(BackgroundsAll.id_night == id_night).all()
    finally:
        db.close()


def get_frames_by_night_filter(id_night: int, id_filter: int) -> list[Frames]:
    db = Session()
    try:
        return db.query(Frames).filter(Frames.id_night == id_night and Frames.id_filtr == id_filter).all()
    finally:
        db.close()


def get_dark_files_logic(request: GetDarkFilesDbRequest) -> Path:

    dark_path = [path.dest for path in get_dark_frames(request.id_night)]
    fit_format = fits_formats[request.fit_format]
    dark_data = get_dark_by_path(dark_path, request.zipped_file, fit_format)

    save_path = show_darks_frames(
        dark_data,
        save_folder=Path(request.save_folder),
        file_name=request.file_name,
        title=request.title,
        row_f=request.row_f,
        column_f=request.column_f,
        figsize=request.figsize
    )

    return save_path


def create_heatmap_logic(request: CreateHeatmapDbRequest):
    frames = get_frames_by_night_filter(request.id_night, request.id_filter)
    frames_path = [frame.dest for frame in frames]
    filter_model = get_filter_matrix_by_id(request.id_filter)
    correct_matrix_path = Path(filter_model.path, filter_model.filename)

    req = CreateHeatmapDbInternal(**request.model_dump())
    req.files_path = frames_path
    req.correct_matrix_path = correct_matrix_path
    recipe = HeatmapRecipe.get_recipe_by_request(req)
    if req.dark:
        recipe.dark_file_path = [path.dest for path in get_dark_frames(req.id_night)]
    print_vars(recipe)
    orchestrator.create_heatmap(recipe)

    return os.path.join(request.save_folder, f'{request.file_name}.png')


# Пример функции, которая выполняет тяжелую операцию по созданию видео
def create_video_db_logic(request: CreateVideoDbRequest):
    frames = get_frames_by_night_filter(request.id_night, request.id_filter)
    frames_path = [frame.dest for frame in frames]
    filter_model = get_filter_matrix_by_id(request.id_filter)
    correct_matrix_path = Path(filter_model.path, filter_model.filename)
    req = CreateVideoDbInternal(**request.model_dump())
    req.files_path = frames_path
    req.correct_matrix_path = correct_matrix_path

    recipe = VideoRecipe.get_recipe_by_request(req)
    if req.dark:
        recipe.dark_file_path = [path.dest for path in get_dark_frames(req.id_night)]


    return orchestrator.create_video(recipe)


def create_video_image_db_logic(request: CreateImageForVideoDbRequest):
    frames = get_frames_by_night_filter(request.id_night, request.id_filter)
    frames_path = [frame.dest for frame in frames]
    filter_model = get_filter_matrix_by_id(request.id_filter)
    correct_matrix_path = Path(filter_model.path, filter_model.filename)
    req = CreateImageForVideoDbInternal(**request.model_dump())
    req.files_path = frames_path
    req.correct_matrix_path = correct_matrix_path

    recipe = VideoRecipe.get_recipe_by_request(req)
    if req.dark:
        recipe.dark_file_path = [path.dest for path in get_dark_frames(req.id_night)]

    print_vars(recipe)
    orchestrator.create_image_for_video(recipe, req.frame_number)


    return  os.path.join(request.save_folder, f'{request.file_name}.png')


def create_image_db_logic(request: CreateImageDbRequest):

    frameModel = get_frame_by_id(request.frameId)
    req = CreateImageDbInternal(**request.model_dump())
    req.files_path = [Path(frameModel.framePath)]
    req.frame_number = 0
    req.correct_matrix_path = Path(frameModel.matrixFolder, frameModel.matrixName)

    recipe = ImageRecipe.get_recipe_by_request(req)
    if req.dark:
        recipe.dark_file_path = [path.dest for path in get_dark_frames(frameModel.id_night)]

    print_vars(recipe)
    orchestrator.create_image(recipe)

    return os.path.join(req.save_folder, f'{req.file_name}.png')


