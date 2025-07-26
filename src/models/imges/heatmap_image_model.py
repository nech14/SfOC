from src.models.imges.img_model import Img
from src.models.recipes.base_recipes_model import BaseRecipes


class HeatmapImage(Img):

    def show(self, recipe: BaseRecipes) -> None:
        pass


    @classmethod
    def create_image(cls):
        pass