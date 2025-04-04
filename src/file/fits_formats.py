
from collections import defaultdict
from src.file import FitsInfoAndor, FitsInfo, FitsInfo2014

fits_formats = defaultdict(lambda: FitsInfo, {
    "FitsInfoAndor": FitsInfoAndor,
    "FitsInfo": FitsInfo,
    "FitsInfo2014": FitsInfo2014,
})
