from typing import Tuple, Union, List

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

from src.models.common_models.hist_limits import HistLimits
from src.models.images_models.abstract_img import AbstractImg

def get_equal_intervals_integers(a, b, n):
    if n < 2:
        return [a] if n == 1 else []

    step = (b - a) // (n - 1)
    return [a + step * i for i in range(n)]


def get_hist_parameters(image: AbstractImg, bins=2000, max_limit=65535) \
        -> Tuple[float, float, float, float]:
    plt.figure(figsize=(10, 10))
    f_data = image.data.flatten()
    # image.show()
    clean_data = image.data.flatten()
    clean_data = clean_data[np.isfinite(clean_data)]
    min_x = np.percentile(clean_data, 1)
    max_x = np.percentile(clean_data, 99)
    if max_x > max_limit: max_x = max_limit

    counts, bin_edges, patches = plt.hist(f_data, bins=bins)
    plt.close()
    return min_x, max_x, 0, max(counts*1.5)


def get_hist_parameters_images(
        img_first: AbstractImg,
        img_second: AbstractImg,
        diff = None,
        bins=2000
) -> Tuple[float, float, float, float, float, float, float]:
    if diff is None:
        diff = img_first.data - img_second.data
    plt.figure(figsize=(10, 10))
    f_data = img_first.data.flatten()
    f_data1 = img_second.data.flatten()
    f_diff = diff.flatten()

    clean_data = img_first.data.flatten()
    clean_data = clean_data[np.isfinite(clean_data)]
    min_x = np.percentile(clean_data, 1) * 2
    max_x = np.percentile(clean_data, 99) * 2

    clean_data1 = img_second.data.flatten()
    clean_data1 = clean_data1[np.isfinite(clean_data1)]
    min_x1 = np.percentile(clean_data1, 1) * 2
    max_x1 = np.percentile(clean_data1, 99) * 2

    clean_diff = diff.flatten()
    clean_diff = clean_diff[np.isfinite(clean_diff)]
    min_d = np.percentile(clean_diff, 1) * 2
    max_d = np.percentile(clean_diff, 99) * 2

    counts, bin_edges, patches = plt.hist(f_data, bins=bins)
    counts1, bin_edges1, patches1 = plt.hist(f_data1, bins=bins)
    counts_d, bin_edges_d, patches_d = plt.hist(f_diff, bins=bins)

    plt.close()

    return min(min_x, min_x1, 0), max(max_x, max_x1), 0, max(max(counts*1.5), max(counts1*1.5)), min(0, min_d), max_d, max(counts_d*1.5)


def create_hists(
        image_first, image_second=None, diff=None, diff1=None,
        hist_limits: HistLimits = HistLimits.get_base_limits(),
        bins=2000, alpha=0.5, show=False,
        figsize_x=16.54, figsize_y=5.12, return_data=False
) -> Union[
    Tuple[
        np.ndarray,
        np.ndarray,
        List[mpatches.Patch]
    ],
    np.ndarray
]:
    #15.36
    fig = plt.figure(figsize=(figsize_x, figsize_y))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.65, 1])

    ax1 = fig.add_subplot(gs[0, 0])
    result_hist = ax1.hist(image_first.flatten(), bins=bins)

    if return_data:
        if show:
            plt.show()
        plt.close()
        return result_hist

    if hist_limits.xmin is not None and hist_limits.xmax is not None:
        ax1.set_xlim(xmin=hist_limits.xmin, xmax=hist_limits.xmax)
    if hist_limits.ymin is not None and hist_limits.ymax is not None:
        ax1.set_ylim(ymin=hist_limits.ymin, ymax=hist_limits.ymax)

    if not image_second is None:
        result_hist1 = ax1.hist(image_second.flatten(), bins=bins, alpha=0.5)

    ax2 = fig.add_subplot(gs[0, 1])
    if diff1 is not None:
        result_hist_diff = ax2.hist(diff1.flatten(), bins=bins)
    else:
        alpha = 1
        result_hist_diff = None
    result_hist_diff1 = ax2.hist(diff.flatten(), bins=2000, alpha=alpha, color="orange")


    if hist_limits.xmin_diff is not None and hist_limits.xmax_diff is not None:
        ax2.set_xlim(xmin=hist_limits.xmin_diff, xmax=hist_limits.xmax_diff)
    if hist_limits.ymin_diff is not None and hist_limits.ymax_diff is not None:
        ax2.set_ylim(ymin=hist_limits.ymin_diff, ymax=hist_limits.ymax_diff)

    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.97, top=0.99, wspace=0.13, hspace=0)

    canvas = plt.gcf().canvas
    canvas.draw()
    rgb_string = canvas.buffer_rgba()

    image_array = np.frombuffer(rgb_string, dtype=np.uint8)
    image_array = image_array.reshape(canvas.get_width_height()[::-1] + (4,))

    if show:
        plt.show()
    else:
        plt.close()

    return image_array[:, :, :3]

