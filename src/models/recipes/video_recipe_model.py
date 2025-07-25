from src.models.recipes.base_recipes_model import BaseRecipes


class VideoRecipe(BaseRecipes):
    first_frame_number: int = 0
    last_frame_number: int | None = None
