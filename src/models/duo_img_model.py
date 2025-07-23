from src.models.dark_data_model import DarkData
from src.models.img_model import Img


class DuoImg:

    def __init__(self):
        self.img_first: Img = None
        self.img_second: Img = None

    def remove_single_pixels(self) -> 'DuoImg':
        self.img_first.remove_single_pixels()
        self.img_second.remove_single_pixels()
        return self

    def dark_frames(self, dark_start: DarkData, dart_end: DarkData) -> 'DuoImg':
        self.img_first.dark_frames(dark_start, dart_end)
        self.img_second.dark_frames(dark_start, dart_end)
        return self

    def correct_matrix(self, correct_matrix, multiplication=True) -> 'DuoImg':
        self.img_first.correct_matrix(correct_matrix, multiplication)
        self.img_second.correct_matrix(correct_matrix, multiplication)
        return self

    def rayleigh(self) -> 'DuoImg':
        self.img_first.rayleigh()
        self.img_second.rayleigh()
        return self

    def cut(self) -> 'DuoImg':
        self.img_first.cut()
        self.img_second.cut()
        return self

