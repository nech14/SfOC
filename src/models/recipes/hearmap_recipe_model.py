from src import logics
from src.models.recipes.base_recipes_model import BaseRecipes


class HeatmapRecipe(BaseRecipes):

    edges: int = 00
    first_frame_number: int = 0
    _last_frame_number: int|None = None
    bins: int = 100
    cmap: str = "viridis"
    counts_checks: int = 4
    check_frame: list[int]|None = None
    result_auto_contrast: bool = False

    def __init__(self, names_files, root_path):
        self.names_files = names_files
        self.root_path = root_path
        self.name = "test1"
        self.file_name = "test10_100b"

    xmin_data: float|None = None
    xmax_data: float|None = None
    ymin_data: float|None = None
    ymax_data: float|None = None

    @property
    def last_frame_number(self):
        if not self._last_frame_number is None:
            return self._last_frame_number
        if self.names_files is None or len(self.names_files)==0:
            self.get_names_files()
        return len(self.names_files)

    def found_limits(self):
        (self.xmin_data, self.xmax_data,
         self.ymin_data, self.ymax_data,
         _, _, _) = logics.get_hist_p(
            self.names_files, self.root_path,
            start_i=self.first_frame_number,
            end_i=self.last_frame_number,
            _zip=self.zipped_file,
            counts_checks=self.counts_checks, bins=self.bins,
            cut=self.cut, percent_to_trim=self.percent_to_trim,
            fit_format=self.fit_format,
            dark=self.dark, dark_name=self.dark_file_name,
            corr_matrix=self.correct_matrix, Rayleigh=self.rayleigh,
            flag_info=self.flag_info, check_frame=self.check_frame,
            data_index=self.data_index,
            remove_single_pixels=self.remove_single_pixels,
            multiplication_on_correct_matrix=self.multiplication_on_correct_matrix
        )
        # self.xmax_data = 10000
        # self.xmin_data = 2000
