from src.models.fits_models.abstract_fits import FitsInfoAbstract


class FitsInfo2014(FitsInfoAbstract):
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
