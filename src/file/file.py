import os
import gzip
import datetime
from pathlib import Path

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


class FitsInfoAndor(FitsInfoBase):

    def __init__(self, info):
        self.SIMPLE = info[0]
        self.BITPIX = info[1]
        self.NAXIS = info[2]
        self.NAXIS1 = info[3]
        self.NAXIS2 = info[4]
        self.NAXIS3 = info[5]
        self.EXTEND = info[6]
        self.HEAD = info[7]
        self.ACQMODE = info[8]
        self.READMODE = info[9]
        self.IMGRECT = info[10]
        self.HBIN = info[11]
        self.VBIN = info[12]
        self.SUBRECT = info[13]
        self.DATATYPE = info[14]
        self.XTYPE = info[15]
        self.XUNIT = info[16]
        self.RAYWAVE = info[17]
        self.CALBWVNM = info[18]
        self.TRIGGER = info[19]
        self.CALIB = info[20]
        self.DLLVER = info[21]
        self.EXPOSURE = info[22]
        self.TEMP = info[23]
        self.READTIME = info[24]
        self.OPERATN = info[25]
        self.GAIN = info[26]
        self.EMREALGN = info[27]
        self.VCLKAMP = info[28]
        self.VSHIFT = info[29]
        self.PREAMP = info[30]
        self.SERNO = info[31]
        self.UNSTTEMP = info[32]
        self.BLCLAMP = info[33]
        self.PRECAN = info[34]
        self.FLIPX = info[35]
        self.FLIPY = info[36]
        self.CNTCVTMD = info[37]
        self.CNTCVT = info[38]
        self.DTNWLGTH = info[39]
        self.SNTVTY = info[40]
        self.SPSNFLTR = info[41]
        self.THRSHLD = info[42]
        self.PCNTENLD = info[43]
        self.NSETHSLD = info[44]
        self.PTNTHLD1 = info[45]
        self.PTNTHLD2 = info[46]
        self.PTNTHLD3 = info[47]
        self.PTNTHLD4 = info[48]
        self.AVGFTRMD = info[49]
        self.AVGFCTR = info[50]
        self.FRMCNT = info[51]
        self.PORTMODE = info[52]
        self.LSHEIGHT = info[53]
        self.LSSPEED = info[54]
        self.LSALTDIR = info[55]
        self.LSCTRL = info[56]
        self.LSDIR = info[57]
        self.FKSMODE = info[58]
        self.FKTMODE = info[59]
        self.USERTXT1 = info[60]
        self.USERTXT2 = info[61]
        self.USERTXT3 = info[62]
        self.USERTXT4 = info[63]
        self.EXPOTIME = info[66]
        self.FRAME = info[67]
        self.ESHTMODE = info[68]
        self.HIERARCH_PREAMPGAINTEXT = info[69]
        self.HIERARCH_SPECTROGRAPHSERIAL = info[70]
        self.HIERARCH_SHAMROCKISACTIVE = info[69]
        self.HIERARCH_SPECTROGRAPHNAME = info[70]
        self.HIERARCH_SPECTROGRAPHISACTIVE = info[71]

    def get_norm_time(self):
        time = self.EXPOTIME
        return time[-8:]

    def get_datetime(self):
        date = str(self.EXPOTIME)
        return datetime.datetime(int(date[:4]), int(date[5: 7]), int(date[8: 10]),
                                 int(date[11: 13]), int(date[14: 16]), int(date[17: 20]))



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


def get_A(CCDGAIN, ROSPEED, DEVICEID="ASI0") -> float:
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


class_registry = {}
class_registry["FitsInfoBase"] = FitsInfoBase
class_registry["FitsInfo"] = FitsInfo
class_registry["FitsInfo2014"] = FitsInfo2014
class_registry["FitsInfoAndor"] = FitsInfoAndor


def get_name_files(folder_path: Path|str="/") -> list[str]:
    files = os.listdir(folder_path)

    names = []

    # Выводим имена файлов
    for file in files:
        names.append(file)
    names.sort()
    return names


def open_gz(gz_file_path: Path|str, _zip=True) -> (list, list):
    if _zip:
        with gzip.open(gz_file_path, 'rb') as gz_file:
            # Чтение файла FITS из архива Gzip

            with fits.open(gz_file) as f:
                return f[0].header, f[0].data
    else:
        with fits.open(gz_file_path) as f:
            return f[0].header, f[0].data


def remove_extensions(file_path: Path|str):
    # Удаляем расширения, пока они есть
    while True:
        file_path, ext = os.path.splitext(file_path)
        if not ext:  # Когда расширений больше нет, завершаем
            break
    return file_path