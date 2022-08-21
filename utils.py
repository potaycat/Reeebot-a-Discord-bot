import cv2
import numpy as np
import requests
import asyncio
from typing import Coroutine


class ImageOpener:
    SIZE_X = 512
    SIZE_Y = 512
    image_: cv2

    async def load_from_url(self, url):
        # https://stackoverflow.com/questions/57539233/how-to-open-an-image-from-an-url-with-opencv-using-requests-from-python
        # TODO async request
        resp = requests.get(url, stream=True).raw
        img = np.asarray(bytearray(resp.read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        self.image_ = img
        self._normalize_size()

    async def load_from_msg(self, msg):
        url = self.__class__.image_url_from_msg(msg)
        await self.load_from_url(url)

    def _normalize_size(self):
        dim = (self.SIZE_X, self.SIZE_Y)
        self.image_ = cv2.resize(self.image_, dim, interpolation=cv2.INTER_AREA)

    @staticmethod
    def image_url_from_msg(msg):
        if p := msg.mentions:
            return p[0].avatar.url
        elif a := msg.attachments:
            return a[0].url
        elif len(i := msg.content.split(" ")) > 1:
            if i[-1].startswith("http"):
                return i[-1]
        return msg.author.avatar.url
