import math
import os
from datetime import datetime
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt, gridspec

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


def get_dark_by_path(
        dark_file_path: list[Path],
        zipped_file: bool=True,
        fit_format: type[FitsInfoAbstract] = FitsInfo
) -> list[DarkData]:
    dark_data = []
    for path in dark_file_path:
        info, data = file.open_gz(path, _zip=zipped_file)
        info = fit_format(info)
        time = info.get_datetime()
        dark_f = DarkData(data, time)
        dark_data.append(dark_f)

    dark_data.sort(key=lambda e: e.time)
    return dark_data


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



def show_darks_frames(
        dark_frames: list[DarkData],
        row_f:int = None,
        column_f: int = None,
        save_folder: Path = None,
        file_name: str = None,
        title: str = None,
        figsize: tuple[float, float] = (12, 12)
) -> Path:
    fig = plt.figure(figsize=figsize)

    if row_f is None and column_f is None:
        row_f = math.ceil(math.sqrt(len(dark_frames)))
        column_f = row_f
    if row_f is None:
        row_f = math.ceil(len(dark_frames)/column_f)
    if column_f is None:
        column_f = math.ceil(len(dark_frames)/row_f)

    gs = gridspec.GridSpec(row_f, column_f+1, figure=fig, width_ratios=[1] * (column_f) + [0.05])
    im = None
    vmin = min(d.frame.min() for d in dark_frames)
    vmax = max(d.frame.max() for d in dark_frames)
    axes = []
    for i, dark in enumerate(dark_frames):
        row = i // column_f
        col = i % column_f
        ax = fig.add_subplot(gs[row, col])
        axes.append(ax)
        im = ax.imshow(dark.frame, vmin=vmin, vmax=vmax)
        ax.set_title(f"{dark.time}")
        ax.invert_yaxis()

    if title:
        fig.suptitle(title)

    # Добавляем colorbar в отдельную колонку
    cax = fig.add_subplot(gs[:, -1])
    cbar = fig.colorbar(im, cax=cax, ax=axes)
    cbar.set_label("Интенсивность", rotation=90)

    plt.tight_layout()

    if save_folder is None:
        save_folder = Path.cwd() / (save_folder or "output")

    save_folder.mkdir(parents=True, exist_ok=True)

    if file_name is None:
        file_name_buf = f"dark_frames_{dark_frames[0].time}_{dark_frames[-1].time}"
    else:
        file_name_buf = file_name

    save_path = save_folder / f"{file_name_buf}.png"
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    return save_path