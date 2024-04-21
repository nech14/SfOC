import os
import gzip
import datetime
from astropy.io import fits


class FitsInfoBase:


    def __init__(self, info):
        self.EXPOTIME = info[0]

    def get_time(self):
        return str(self.EXPOTIME)[-6:]

    def get_norm_time(self):
        time = self.get_time()
        return time[:2] + ':' + time[2:4] + ':' + time[4:]

    def get_datetime(self):
        date = str(self.EXPOTIME)
        return datetime.datetime(int(date[:4]), int(date[4: 6]), int(date[6: 8]),
                                 int(date[8: 10]), int(date[10: 12]), int(date[12: 14]))


class FitsInfo(FitsInfoBase):

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


class FitsInfo2014(FitsInfoBase):

    def __init__(self, info):
        self.SIMPLE = info[0]
        self.BITPIX = info[1]
        self.NAXIS = info[2]
        self.NAXIS1 = info[3]
        self.NAXIS2 = info[4]
        self.BZERO = info[5]
        self.BSCALE = info[6]
        self.DATAMIN = info[7]
        self.DATAMAX = info[8]
        self.INSTRUME = info[9]
        self.EXPTIME = info[10]
        self.EXPOTIME = info[11][:4] + info[11][5:7] + info[11][8:10] + info[11][11:13] + info[11][14:16] + info[11][17:19]
        self.XPIXSZ = info[12]
        self.YPIXSZ = info[13]
        self.XBINNING = info[14]
        self.YBINNING = info[15]
        self.XORGSUBF = info[16]
        self.YORGSUBF = info[17]
        self.XPOSSUBF = info[18]
        self.YPOSSUBF = info[19]
        self.CBLACK = info[20]
        self.CWHITE = info[21]
        self.CCD_TEMP = info[22]
        self.SWCREATE = info[23]


def get_A(CCDGAIN, ROSPEED, DEVICEID="ASI0"):
    if "ASI0" in DEVICEID:
        if "2MHz" in ROSPEED:
            A = [0.255, 0.508, 1.]
            return A[CCDGAIN-1]
        elif "100kHz" in ROSPEED:
            A = [0.252, 0.503, 1.]
            return A[CCDGAIN-1]

    elif "ASI1" in DEVICEID:
        if "2MHz" in ROSPEED:
            A = [0.258, 0.512, 1.]
            return A[CCDGAIN-1]
        elif "100kHz" in ROSPEED:
            A = [0.253, 0.503, 1.]
            return A[CCDGAIN-1]


def get_name_file(folder_path="/"):
    files = os.listdir(folder_path)

    names = []

    # Выводим имена файлов
    for file in files:
        names.append(file)
    return names


def open_gz(gz_file_path, _zip=True):
    if _zip:
        with gzip.open(gz_file_path, 'rb') as gz_file:
            # Чтение файла FITS из архива Gzip

            with fits.open(gz_file) as f:
                return f[0].header, f[0].data
    else:
        with fits.open(gz_file_path) as f:
            return f[0].header, f[0].data