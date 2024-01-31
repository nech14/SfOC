
import os
import gzip
from astropy.io import fits


class FitsInfo:
    def __init__(self, info):
        self.SIMPLEX = info[0]
        self.BITRIX = info[1]
        self.NAXIS = info[2]
        self.NAXIS1 = info[3]
        self.NAXIS2 = info[4]
        self.BSCALE = info[5]
        self.BZERO = info[6]
        self.DATAMAX = info[7]
        self.DATAMIN = info[8]
        self.HISTORY = info[9]
        self.EXPOTIME = info[10]
        self.BINNING = info[11]
        self.BITDEPTH = info[12]
        self.CCDGAIN = info[13]
        self.CCDTEMP = info[14]
        self.EXPOSURE = info[15]
        self.ROSPEED = info[16]
        self.SEQNO = info[17]
        self.SITEID = info[18]
        self.DEVICEID = info[19]
        self.LATITUDE = info[20]
        self.LONGITUD = info[21]
        self.FILTERWA = info[22]
        self.FILTERPO = info[23]
        self.FWTEMP = info[24]
        self.VERSION = info[25]


def get_name_file(folder_path="/"):
    files = os.listdir(folder_path)

    names = []

    # Выводим имена файлов
    for file in files:
        names.append(file)
    return names


def open_gz(gz_file_path):
    with gzip.open(gz_file_path, 'rb') as gz_file:
        # Чтение файла FITS из архива Gzip
        with fits.open(gz_file) as f:
            return f[0].header, f[0].data

