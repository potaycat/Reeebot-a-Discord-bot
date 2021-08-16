# Source: https://github.com/CairX/extract-colors-py

import math
import collections
import numpy as np
import cv2
from convcolors import rgb_to_lab
try:
    from sklearn import cluster
except ImportError:
    pass

DEFAULT_TOLERANCE = 32
FILE_PATH = "modules/image_manip/comvis/"


if __name__ != '__main__':
    from utils import ImageOpener

    class ColorQuantizer(ImageOpener):

        def kmeans_quantize(self, n_clusters=8):
            rgb_mat = np.reshape(self._image, (self.SIZE_Y*self.SIZE_X, 3))
            km = cluster.MiniBatchKMeans(n_clusters, random_state=0)
            y_cl = km.fit_predict(rgb_mat)
            self.color_ls = km.cluster_centers_

            
        def nearest_color_quantize(self, tolerance=DEFAULT_TOLERANCE, limit=None):
            pixels = np.reshape(self._image, (self.SIZE_Y*self.SIZE_X, 3))
            pixel_count = len(pixels)
            colors = _count_colors(pixels)
            colors = _compress(colors, tolerance)

            if limit:
                limit = min(int(limit), len(colors))
                colors = colors[:limit]

            self.color_ls = colors


        def export_png(self):
            display = None
            for color in self.color_ls:
                color = np.array([color]).astype(np.uint8)
                color_mat = np.repeat(color, 3000, 0)
                color_mat = np.reshape(color_mat, (50,60,3))
                if display is None:
                    display = color_mat
                else:
                    display = cv2.hconcat([display, color_mat])
            exprt_path = FILE_PATH+"palette.png"
            cv2.imwrite(exprt_path, cv2.cvtColor(display, cv2.COLOR_RGB2BGR))
            return exprt_path


class Color:
    def __init__(self, rgb=None, lab=None, count=0):
        self.rgb = rgb
        self.lab = lab
        self.count = count
        self.compressed = False

    def __lt__(self, other):
        return self.count < other.count


def cie76(c1, c2):
    l = c2[0] - c1[0]
    a = c2[1] - c1[1]
    b = c2[2] - c1[2]
    return math.sqrt((l * l) + (a * a) + (b * b))


def _count_colors(pixels):
    counter = collections.defaultdict(int)
    for color in pixels:
        counter[tuple(color)] += 1

    colors = []
    for rgb, count in counter.items():
        lab = rgb_to_lab(rgb)
        colors.append(Color(rgb=rgb, lab=lab, count=count))

    return colors


def _compress(colors, tolerance):
    colors.sort(reverse=True)

    if tolerance <= 0:
        return colors

    i = 0
    while i < len(colors):
        larger = colors[i]

        if not larger.compressed:
            j = i + 1
            while j < len(colors):
                smaller = colors[j]

                if not smaller.compressed and cie76(
                        larger.lab, smaller.lab) < tolerance:
                    larger.count += smaller.count
                    smaller.compressed = True

                j += 1
        i += 1

    colors = [color.rgb for color in colors if not color.compressed]
    colors.sort(reverse=True)

    return colors



if __name__ == '__main__':
    path = "D:/Users/long/Downloads/20210709_000317.jpg"
    rgb_mat = cv2.imread(path)
    height = width = 512
    if rgb_mat.shape[0] > height or rgb_mat.shape[1] > width:
        rgb_mat = cv2.resize(rgb_mat, (width, height), interpolation=cv2.INTER_NEAREST)
    # rgb_mat = cv2.cvtColor(rgb_mat, cv2.COLOR_BGR2RGB)
    cv2.imshow('img', rgb_mat)
    cv2.waitKey(0)
    
    rgb_mat = np.reshape(rgb_mat, (width*height, 3))
    cl = cluster.MiniBatchKMeans(8, random_state=0)
    y_cl = cl.fit_predict(rgb_mat)

    display = None
    for color in cl.cluster_centers_:
        color = np.array([color]).astype(np.uint8)
        # print(color)
        color_mat = np.repeat(color, 3000, 0)
        color_mat = np.reshape(color_mat, (50,60,3))
        if display is None:
            display = color_mat
        else:
            display = cv2.hconcat([display, color_mat])
    exprt_path = FILE_PATH+"palette.png"
    print(display)
    cv2.imwrite(exprt_path, display)
    cv2.imshow('color strip', display)
    cv2.waitKey(0)
