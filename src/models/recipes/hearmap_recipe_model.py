from src import logics
from src.models.hist_limits import HistLimits
from src.models.recipes.base_recipes_model import BaseRecipes
from src.pipeline.utils.helpers import get_equal_intervals_integers

class HeatmapRecipe(BaseRecipes):

    edges: int = 00
    first_frame_number: int = 0
    _last_frame_number: int|None = None
    bins: int = 100
    cmap: str = "viridis"
    counts_checks: int = 4
    need_check_frames: list[int] | None = None
    result_auto_contrast: bool = False
    hist_limits: HistLimits = None

    def __init__(self, names_files, root_path):
        self.names_files = names_files
        self.root_path = root_path
        self.name = "test1"
        self.file_name = "test10_100b"

    @property
    def last_frame_number(self):
        if not self._last_frame_number is None:
            return self._last_frame_number
        if self.names_files is None or len(self.names_files)==0:
            self.get_names_files()
        return len(self.names_files)

    def get_check_frame(self):
        end_i = self.last_frame_number
        if end_i is None:
            end_i = len(self.names_files) - 1

        start_i = self.first_frame_number
        count_frame = end_i - self.first_frame_number

        check_frame = self.need_check_frames
        if check_frame is None:
            check_frame = []
        elif isinstance(check_frame, int):
            check_frame = [check_frame]

        if count_frame > self.counts_checks and self.counts_checks > 0:
            check_frame_buf = set(check_frame).union(get_equal_intervals_integers(start_i, end_i - 1, self.counts_checks))
            check_frame = list(check_frame_buf)
        elif len(check_frame) == 0:
            check_frame = range(start_i, end_i)

        self.need_check_frames = check_frame.copy()
        return self.need_check_frames