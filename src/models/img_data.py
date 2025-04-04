from src.file import FitsInfo
from src.file.file import FitsInfoBase


class ImgData:
    info: FitsInfoBase
    data = []
    path = ""
    name = ""

    def __init__(self, header, data, fit_format:FitsInfoBase=FitsInfo, data_index=None):
        self.info = fit_format(header)
        self.data = data if data_index is None else data[data_index]

