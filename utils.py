import cv2
import numpy as np
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()


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

    async def load_from_msg(self, msg, mention=None, attch_url=None):
        ava_url = lambda user: user.avatar.url.replace(".gif", ".png").replace(
            "size=1024", "size=512"
        )
        if mention:
            url = ava_url(mention)
        elif attch_url:
            url = attch_url
        elif x := msg.mentions:
            url = ava_url(x[0])
        elif x := msg.attachments:
            url = x[0].url
        elif len(x := msg.content.split(" ")) > 1:
            if x[-1].startswith("http"):
                url = x[-1]
        else:
            url = ava_url(msg.author)
        await self.load_from_url(url)

    def _normalize_size(self):
        dim = (self.SIZE_X, self.SIZE_Y)
        self.image_ = cv2.resize(self.image_, dim, interpolation=cv2.INTER_AREA)


async def arun_blockings(*blockings):
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, *fun) for fun in blockings]
    results = await asyncio.gather(*tasks)
    return results


async def arun_blocking(blocking):
    (result,) = await arun_blockings(blocking)
    return result
