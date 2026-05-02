
from collections import defaultdict

from src.models.fits_models.fits_andor import FitsInfoAndor
from src.models.fits_models.fits import FitsInfo
from src.models.fits_models.fits_2014 import FitsInfo2014

fits_formats = defaultdict(lambda: FitsInfo, {
    "FitsInfoAndor": FitsInfoAndor,
    "FitsInfo": FitsInfo,
    "FitsInfo2014": FitsInfo2014,
})
