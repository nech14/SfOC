import base64
from io import BytesIO

import numpy as np
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, APIRouter
from fastapi.encoders import jsonable_encoder
from matplotlib import pyplot as plt
from starlette.responses import HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from api.schemas.auto_contrast_command_request import AutoContrastCommandRequest
from api.schemas.correct_matrix_request import CorrectMatrixRequest
from api.schemas.cut_command_request import CutCommandRequest
from api.schemas.dark_command_request import DarkCommandRequest
from api.schemas.load_command_request import LoadCommandRequest
from api.schemas.save_data_request import SaveDataRequest
from api.schemas.save_img_request import SaveImgRequest
from src.editor.commands.auto_contrast_command import AutoContrastCommand
from src.editor.commands.correct_matrix_command import CorrectMatrixCommand
from src.editor.commands.cut_command import CutCommand
from src.editor.commands.dark_command import DarkCommand
from src.editor.commands.load_command import LoadCommand
from src.editor.commands.rayleigh_command import RayleighCommand
from src.editor.commands.remove_single_pixels_command import RemoveSinglePixelsCommand
from src.editor.commands.save_data_command import SaveDataCommand
from src.editor.commands.save_img_command import SaveImgCommand
from src.editor.commands.select_command import SelectCommand
from src.editor.commands.undo_command import UndoCommand
from src.editor.editor import Editor
from src.file import FitsInfo
from src.file.fits_formats import fits_formats

app = FastAPI()
rout_root = ""
editor: Editor|None = None


app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="api/templates")

def check_editor():
    global editor
    if editor is None:
        editor = Editor()
        # raise HTTPException(
        #     status_code = status.HTTP_403_FORBIDDEN,
        #     detail="Editor is not set"
        # )
    return True


@app.get(f"{rout_root}/create")
async def create_editor():
    global editor
    editor = Editor()

    return {"status": "editor created"}

@app.get(f"{rout_root}/undo")
async def undo():
    editor.executeCommand(
        UndoCommand(
            editor
        )
    )
    return {"status": "editor undo"}



@app.get(f"{rout_root}/view", response_class=HTMLResponse)
async def view_editor_page(request: Request, auth: bool = Depends(check_editor)):
    try:
        img_array, _ = editor.view()  # Игнорируем data, так как он не нужен для шаблона

        # Рисуем картинку из массива
        fig, ax = plt.subplots()
        ax.imshow(img_array, cmap='gray')
        ax.axis('off')

        # Сохраняем в буфер
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)

        # Кодируем в base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        img_data_uri = f"data:image/png;base64,{img_base64}"

        return templates.TemplateResponse("view.html", {
            "request": request,
            "img": img_data_uri,
            "data": ""  # Передаем пустую строку вместо data, если оно не нужно
        })
    except Exception as e:
        print(f"Ошибка в view: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing view: {str(e)}")


@app.get(f"{rout_root}/view_data")
async def view_editor_data(auth: bool = Depends(check_editor)):
    try:
        img_array, _ = editor.view()  # Игнорируем data
        print(f"Тип img_array: {type(img_array)}, Размер: {img_array.shape if hasattr(img_array, 'shape') else 'Нет shape'}")

        # Проверяем, что img_array валиден
        if img_array is None or not isinstance(img_array, np.ndarray):
            raise ValueError("img_array пустой или не является numpy массивом")

        # Рисуем картинку из массива
        fig, ax = plt.subplots()
        ax.imshow(img_array, cmap='gray')
        ax.axis('off')

        # Сохраняем в буфер
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)

        # Кодируем в base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        img_data_uri = f"data:image/png;base64,{img_base64}"

        response = {
            "img": img_data_uri
        }

        return response

    except Exception as e:
        print(f"Ошибка в view_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get(f"{rout_root}/clear")
async def clear(auth: bool = Depends(check_editor)):
    editor.clear()
    return {"status": "success"}


@app.post(f"{rout_root}/load")
async def load_data(
        request: LoadCommandRequest,
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        LoadCommand(
            editor,
            root_path=request.root_path,
            names_files=request.names_files,
            start_file=request.start_file,
            end_file=request.end_file,
            _zip=request._zip,
            fit_format=fits_formats[request.fit_format],
            data_index=request.data_index
        )
    )
    return {"status": "success"}


@app.get(f"{rout_root}/select")
async def select_data(
        index: int = Query(..., ge=0),
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        SelectCommand(
            editor,
            index
        )
    )
    return {"status": f"{len(editor.datas)}"}


@app.get(f"{rout_root}/select_index")
async def select_index(
        auth: bool = Depends(check_editor)
):
    index = editor.get_target_index()
    return {"status": f"{index}"}


@app.get(f"{rout_root}/count_all_datas")
async def count_all_datas(
        auth: bool = Depends(check_editor)
):
    count = len(editor.datas)
    return {"status": f"{count}"}


@app.post(f"{rout_root}/save_img")
async def save_img(
        request: SaveImgRequest,
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        SaveImgCommand(
            editor,
            save_folder=request.save_folder,
            title = request.title,
            file_name = request.file_name,
            figsize = request.figsize,
            dpi = request.dpi,
            cmap = request.cmap,
            axis = request.axis,
            bbox_inches = request.bbox_inches
        )
    )
    return {"status": "success"}


@app.post(f"{rout_root}/save_data")
async def save_data(
        request: SaveDataRequest,
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        SaveDataCommand(
            editor,
            save_folder=request.save_folder,
            name_file=request.name_file
        )
    )
    return {"status": "success"}


@app.get(f"{rout_root}/download_data")
async def download_data(
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        SaveDataCommand(
            editor,
            save_folder="buf",
            name_file="../buf"
        )
    )
    file_path = f"../buf/buf.pkl"

    return FileResponse(
        path=file_path,
        filename="processed_result.pkl",  # имя файла при скачивании
        media_type="application/octet-stream"
    )



@app.post(f"{rout_root}/cut")
async def cut(
        request:CutCommandRequest,
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        CutCommand(
            editor,
            percent_to_trim=request.percent_to_trim
        )
    )
    return {"status": "success"}


@app.get(f"{rout_root}/dark_indexes")
async def dark_indexes(
        index_start: int | None = Query(..., ge=None),
        index_end: int | None = Query(..., ge=None),
        auth: bool = Depends(check_editor)):

    editor.dark_end_start_index = index_start
    editor.dark_start_end_index = index_end

    return {"status": "success"}


@app.post(f"{rout_root}/dark")
async def dark(
        request:DarkCommandRequest,
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        DarkCommand(
            editor,
            names=request.names,
            root_path = request.root_path,
            file_name = request.file_name,
            _zip = request._zip,
            fit_format = fits_formats[request.fit_format]
        )
    )

    return {"status": "success"}


@app.get(f"{rout_root}/rayleigh")
async def rayleigh(auth: bool = Depends(check_editor)):
    editor.executeCommand(
        RayleighCommand(
            editor
        )
    )

    return {"status": "success"}


@app.get(f"{rout_root}/remove_single_pixels")
async def remove_single_pixels(auth: bool = Depends(check_editor)):
    editor.executeCommand(
        RemoveSinglePixelsCommand(
            editor
        )
    )

    return {"status": "success"}


@app.post(f"{rout_root}/auto_contrast")
async def auto_contrast(
        request:AutoContrastCommandRequest,
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        AutoContrastCommand(
            editor,
            auto_contrast_percentiles=request.auto_contrast_percentiles
        )
    )

    return {"status": "success"}


@app.post(f"{rout_root}/corr_matrix")
async def correct_matrix(
        request: CorrectMatrixRequest,
        auth: bool = Depends(check_editor)
):
    editor.executeCommand(
        CorrectMatrixCommand(
            editor,
            request.correct_matrix,
            request.multiplication_on_correct_matrix
        )
    )


