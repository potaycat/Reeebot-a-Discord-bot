import requests
import json
from random import randint


class PixivApiUtilizer():
    """
        Has all the function for `r!pixiv`
    """
    def getSearchRes(tags="", isNSFW=False):
        if len(tags) == 0:
            return

        mode = 'r18' if isNSFW else 'safe'
        tags = tags.replace(' ', '%20')
        reqUrl = f"https://www.pixiv.net/ajax/search/artworks/{tags}?order=date_d&mode={mode}&p=1&s_mode=s_tag&type=all&lang=en"

        res = requests.get(reqUrl)
        res = json.loads(res.text)
        try:
            res = res['body']['illustManga']['data']
            res = res[ randint(0, len(res)-1) ] ['id']
            # res = res[0]['illustId']
        except:
            return "Can't find any"
        res = f"https://www.pixiv.net/en/artworks/{res}"
        
        return res
