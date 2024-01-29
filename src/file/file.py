
import os
import gzip
from astropy.io import fits

def get_name_file(folder_path="/"):
    files = os.listdir(folder_path)

    names = []

    # Выводим имена файлов
    for file in files:
        names.append(file)
        print(file)
    return names

def open_gz(gz_file_path):
    with gzip.open(gz_file_path, 'rb') as gz_file:
        # Чтение файла FITS из архива Gzip
        with fits.open(gz_file) as f:
            return f[0].data
