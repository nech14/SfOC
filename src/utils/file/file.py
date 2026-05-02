import os
import gzip
from pathlib import Path
from astropy.io import fits

def get_A(CCDGAIN, ROSPEED, DEVICEID="ASI0") -> float|None:
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


def remove_extensions(file_path: Path|str) -> str:
    # Удаляем расширения, пока они есть
    while True:
        file_path, ext = os.path.splitext(file_path)
        if not ext:  # Когда расширений больше нет, завершаем
            break
    return file_path