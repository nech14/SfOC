import os
from datetime import datetime
from pathlib import Path

import numpy as np

from src.models.common_models.dark_data_model import DarkData
from src.models.fits_models.abstract_fits import FitsInfoAbstract
from src.models.fits_models.fits import FitsInfo
from src.utils.file import file


def get_dark(
        names: list[str],
        new_path: Path,
        check_name: str = "DARK",
        _zip: bool = True,
        fit_format: type[FitsInfoAbstract] = FitsInfo
) -> list[DarkData]:
    buf = []
    if check_name in names[0]:
        name_path = Path(new_path, names[0])
        info, data = file.open_gz(name_path, _zip=_zip)
        time = fit_format(info).get_datetime()
        dark_data = DarkData(data, time)
        buf.append(dark_data)
    else:
        return []

    for name in names[1:]:
        if not check_name in name:
            break

        name_path = Path(new_path, name)
        info, data = file.open_gz(name_path, _zip=_zip)
        time = fit_format(info).get_datetime()
        dark_data = DarkData(data, time)

        buf.append(dark_data)

    return buf

def get_dark_avg(
        names: list[str],
        root_path: Path,
        dark_name: str = "DARK",
        _zip: bool = True,
        fit_format: type[FitsInfoAbstract] = FitsInfo
) -> DarkData:
    dark_datas = get_dark(names, root_path, dark_name, _zip=_zip, fit_format=fit_format)
    datas = [data.frame for data in dark_datas]
    data_avg = (np.mean(datas, axis=0))

    # Получаем среднее время в секундах
    average_time_seconds = sum(dd.time for dd in dark_datas) / len(dark_datas)

    # Преобразовываем среднее значение времени обратно в формат datetime.datetime
    time_avg = datetime.fromtimestamp(average_time_seconds)

    return DarkData(data_avg, time_avg)


def subtract_noise_frame(dark_start: DarkData, dark_end: DarkData, data, date_time: datetime):
    k1 = (date_time - dark_start.time) / (dark_end.time-dark_start.time)
    k2 = (dark_end.time - date_time) / (dark_end.time-dark_start.time)

    fix_data = data.copy()
    fix_data = fix_data - (dark_start.frame*k2 + dark_end.frame*k1)/2
    return fix_data