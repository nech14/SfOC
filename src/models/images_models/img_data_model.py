from src.models.fits_models.abstract_fits import FitsInfoAbstract
from src.models.fits_models.fits import FitsInfo


class ImgData:
    info: FitsInfoAbstract
    data = []
    path = ""
    name = ""

    def __init__(self, header, data, fit_format:FitsInfoAbstract=FitsInfo, data_index=None):
        self.info = fit_format(header)
        self.data = data if data_index is None else data[data_index]

