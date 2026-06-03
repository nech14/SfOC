import os
from pathlib import Path


def print_vars(model):
    for k, v in vars(model).items():
        print(f"{k} = {v}")

def get_vars_str(model) -> str:
    result = ""
    for k, v in vars(model).items():
        result += f"{k} = {v}\n"
    return result

def delete_file(path: Path | str):
    if isinstance(path, str):
        path = Path(path)

    try:
        os.remove(path)
    except FileNotFoundError:
        print(f"File {path} was not found.")