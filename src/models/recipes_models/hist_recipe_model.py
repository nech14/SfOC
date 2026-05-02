from src.models.common_models.hist_limits import HistLimits
from src.models.recipes_models.base_recipes_model import BaseRecipes
from src.utils.logics import old_logicks
from src.utils.logics.work_with_hist import get_equal_intervals_integers


class HistRecipe(BaseRecipes):
    edges: int = 0
    _first_frame_number: int = 0
    _last_frame_number: int | None = None
    bins: int = 1000
    hist_limits: HistLimits = None
    counts_checks: int = 4
    need_check_frames: list[int] | None = None
    diff_limits: tuple[float, float] = [-500, 500]

    @property
    def first_frame_number(self):
        if self._first_frame_number is None:
            self._first_frame_number = 0
        return self._first_frame_number + self.edges

    @first_frame_number.setter
    def first_frame_number(self, value):
        self._first_frame_number = value

    @property
    def last_frame_number(self):
        if self._last_frame_number is None:
            self._last_frame_number = self.get_frames_len()
        return self._last_frame_number - self.edges

    @last_frame_number.setter
    def last_frame_number(self, value):
        self._last_frame_number = value


    def get_check_frame(self):
        end_i = self.last_frame_number
        if end_i is None:
            end_i = len(self.files_names) - 1

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

        self.need_check_frames = check_frame
        return self.need_check_frames

    def found_limits(self):
        (self.xmin_data, self.xmax_data,
         self.ymin_data, self.ymax_data,
         self.xmin_diff, self.xmax_diff, self.ymax_diff) = old_logicks.get_hist_p(
            self.files_names, self.root_path,
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