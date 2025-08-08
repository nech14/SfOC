from typing import Tuple


class HistLimits():
    buf_min_x = []
    buf_max_x = []
    buf_min_y = []
    buf_max_y = []
    buf_min_d = []
    buf_max_d = []
    buf_min_dy = []
    buf_max_dy = []

    def add_min_x(self, value):
        self.buf_min_x.append(value)

    def add_max_x(self, value):
        self.buf_max_x.append(value)

    def add_min_y(self, value):
        self.buf_min_y.append(value)

    def add_max_y(self, value):
        self.buf_max_y.append(value)

    def add_min_d(self, value):
        self.buf_min_d.append(value)

    def add_max_d(self, value):
        self.buf_max_d.append(value)

    def add_min_dy(self, value):
        self.buf_min_dy.append(value)

    def add_max_dy(self, value):
        self.buf_max_dy.append(value)

    def get_limits(self) -> Tuple[float, float, float, float, float, float, float]:
        return (min(self.buf_min_x), max(self.buf_max_x),
                min(self.buf_min_y), max(self.buf_max_y),
                min(self.buf_min_d), max(self.buf_max_d), max(self.buf_max_dy))

    def add_limits(
            self,
            min_x:float, max_x:float,
            min_y:float, max_y:float,
            min_d:float, max_d:float,
            max_dy:float
    ):
        self.add_min_x(min_x)
        self.add_max_x(max_x)
        self.add_min_y(min_y)
        self.add_max_y(max_y)
        self.add_min_d(min_d)
        self.add_max_d(max_d)
        self.add_max_dy(max_dy)

    @property
    def xmax(self) -> float|None:
        return max(self.buf_max_x)