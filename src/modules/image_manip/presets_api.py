import requests
from utils import img_url_from_msg, alt_thread
from .consts import FILE_PATH, KALEIDO_API_KEY


@alt_thread
def remove_bg(msg, mention, attch_url):
    x = img_url_from_msg(msg, mention, attch_url)
    x = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        data={"image_url": x, "size": "auto"},
        headers={"X-Api-Key": KALEIDO_API_KEY},
    )
    if x.status_code == requests.codes.ok:
        out_p = FILE_PATH + "no-bg.png"
        with open(out_p, "wb") as f:
            f.write(x.content)
            return out_p
    else:
        raise Exception("Error:", x.status_code, x.text)
