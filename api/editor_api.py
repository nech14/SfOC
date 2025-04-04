
from fastapi import FastAPI, Depends, HTTPException, status

from src.editor.commands.cut_command import CutCommand
from src.editor.editor import Editor

app = FastAPI()
rout_root = ""
editor: Editor

def check_editor():
    if editor is None:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Editor is not set"
        )
    return True


@app.get(f"{rout_root}/create")
async def create_editor():
    global editor
    editor = Editor()

    return {"status": "editor created"}


@app.get(f"{rout_root}/view")
async def view_editor(auth: bool = Depends(check_editor)):
    pass


@app.get(f"{rout_root}/clear")
async def clear(auth: bool = Depends(check_editor)):
    pass


@app.get(f"{rout_root}/load")
async def load_data(auth: bool = Depends(check_editor)):
    pass


@app.get(f"{rout_root}/save")
async def save(auth: bool = Depends(check_editor)):
    pass


@app.get(f"{rout_root}/cut")
async def cut(auth: bool = Depends(check_editor)):
    editor.executeCommand(
        CutCommand(editor)
    )
    pass


@app.get(f"{rout_root}/dark")
async def dark(auth: bool = Depends(check_editor)):
    pass


@app.get(f"{rout_root}/rayleigh")
async def rayleigh(auth: bool = Depends(check_editor)):
    pass


@app.get(f"{rout_root}/remove_single_pixels")
async def remove_single_pixels(auth: bool = Depends(check_editor)):
    pass


@app.get(f"{rout_root}/auto_contrast")
async def auto_contrast(auth: bool = Depends(check_editor)):
    pass




