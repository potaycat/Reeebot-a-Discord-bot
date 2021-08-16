import cv2
import numpy as np
import requests


class ImageOpener():
    SIZE_X = 512
    SIZE_Y = 512
    _image: cv2

    def get_img(self):
        return self._image

    def open(self, file_path):
        self._image = cv2.imread(file_path, flags=cv2.IMREAD_UNCHANGED)
        self._normalize_size()

    def open_from_url(self, url):
        '''https://stackoverflow.com/questions/57539233/how-to-open-an-image-from-an-url-with-opencv-using-requests-from-python'''
        resp = requests.get(url, stream=True).raw
        img = np.asarray(bytearray(resp.read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        self._image = img
        self._normalize_size()

    def _normalize_size(self):
        dim = (self.SIZE_X, self.SIZE_Y)
        self._image = cv2.resize(
            self._image, dim, interpolation=cv2.INTER_AREA)

    
    def image_url_from_msg(self, msg):
        if p := msg.mentions:
            return p[0].avatar_url
        elif a := msg.attachments:
            return a[0].url
        elif len(i := msg.content.split(' ')) > 1:
            if i[-1].startswith("http"):
                return i[-1]
        return msg.author.avatar_url
