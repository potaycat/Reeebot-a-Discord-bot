import numpy as np
import cv2
from random import randint, choice
import os
from utils import ImageOpener


FILE_PATH = "modules/image_manip/comvis/"


class ImageFilterer(ImageOpener):

    def deepfry(self):
        dank_set = os.listdir(FILE_PATH+'emoji/dank/')
        for i in range(7):
            self.emoji_overlay(FILE_PATH+'emoji/dank/' +
                               choice(dank_set), (80, 72))
        self.over_sharpen()
        self.turn_hot()

    def wholesome(self):
        wholesome_set = os.listdir(FILE_PATH+'emoji/wholesome/')
        for i in range(30):
            self.emoji_overlay(
                f'{FILE_PATH}emoji/wholesome/{choice(wholesome_set)}')
        self.radial_blur()

    async def export_png(self, fname):
        exprt_path = f"{FILE_PATH}{fname}.png"
        cv2.imwrite(exprt_path, self.image_)
        return exprt_path

    def _rotate_image(self, img, angle):
        image_center = tuple(np.array(img.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(
            img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

    def _random_loc(self, margin_x, margin_y):
        pos = (
            randint(0, self.image_.shape[0] - margin_x - 1),
            randint(0, self.image_.shape[1] - margin_y - 1)
        )
        # print(pos)
        return pos

    def emoji_overlay(self, src, size=(64, 64)):
        src = cv2.imread(src, -1)
        src = self._rotate_image(src, randint(-75, 75))
        src = cv2.resize(src, size, interpolation=cv2.INTER_AREA)
        x_offset, y_offset = self._random_loc(*src.shape[:2])

        y1, y2 = y_offset, y_offset + src.shape[0]
        x1, x2 = x_offset, x_offset + src.shape[1]

        alpha_s = src[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(0, 3):
            self.image_[y1:y2, x1:x2, c] = (alpha_s * src[:, :, c] +
                                            alpha_l * self.image_[y1:y2, x1:x2, c])

        # img[y_offset:y_offset+src.shape[0], x_offset:x_offset+src.shape[1]] = src

    def over_sharpen(self):
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img = cv2.filter2D(self.image_, -1, kernel)
        img = cv2.addWeighted(img, 4, cv2.blur(img, (30, 30)), -4, 128)
        self.image_ = img

    def turn_hot(self):
        # img = cv2.LUT(img, lut[, dst[, interpolation]])
        hot_overlay = cv2.applyColorMap(self.image_, cv2.COLORMAP_HOT)
        self.image_ = cv2.addWeighted(self.image_, 0.6, hot_overlay, 0.4, 0)

    def motion_blur(self):  # not used
        size = 55

        # generating the kernel
        kernel_motion_blur = np.zeros((size, size))
        kernel_motion_blur[int((size-1)/2), :] = np.ones(size)
        kernel_motion_blur = kernel_motion_blur / size

        # applying the kernel to the input image
        img = cv2.filter2D(img, -1, kernel_motion_blur)

    # https://stackoverflow.com/questions/7607464/implement-radial-blur-with-opencv
    def radial_blur(self):
        img = self.image_
        w, h = img.shape[:2]

        center_x = w / 2
        center_y = h / 2
        blur = 0.01
        iterations = 7

        growMapx = np.tile(
            np.arange(h) + ((np.arange(h) - center_x)*blur), (w, 1)).astype(np.float32)
        shrinkMapx = np.tile(
            np.arange(h) - ((np.arange(h) - center_x)*blur), (w, 1)).astype(np.float32)
        growMapy = np.tile(np.arange(
            w) + ((np.arange(w) - center_y)*blur), (h, 1)).transpose().astype(np.float32)
        shrinkMapy = np.tile(np.arange(
            w) - ((np.arange(w) - center_y)*blur), (h, 1)).transpose().astype(np.float32)

        for i in range(iterations):
            tmp1 = cv2.remap(img, growMapx, growMapy, cv2.INTER_LINEAR)
            tmp2 = cv2.remap(img, shrinkMapx, shrinkMapy, cv2.INTER_LINEAR)
            img = cv2.addWeighted(tmp1, 0.5, tmp2, 0.5, 0)

        self.image_ = img
