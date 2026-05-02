from pathlib import Path

from src.models.recipes_models.hist_recipe_model import HistRecipe

class HeatmapRecipe(HistRecipe):
    cmap: str = "viridis"
    cmap_under: str = None #'#1a1a1a'
    result_auto_contrast: bool = False

    def __init__(self, names_files=None, root_path=None):
        self.names_files: list[str] = names_files
        self.root_path: Path = root_path
        self.title: str = "test1"
        self.file_name = "buf_3"
