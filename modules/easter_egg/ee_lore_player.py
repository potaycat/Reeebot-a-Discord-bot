import os
import json
import re

FILE_PATH = "data/ee_lores/"


class LorePlayer:
    """
    Easter egg dialog player for specific friends
    """

    snowflake = "0"
    file_path = ""
    cur_line = 0

    def __init__(self, snwflk="", cur_line=0):
        self.snowflake = snwflk
        self.file_path = f"{FILE_PATH}active/{snwflk}.txt"
        self.cur_line = cur_line

    def get_cur_line(self):
        return self.cur_line

    def readline(self, ip):
        with open(self.file_path) as f:
            for i, line in enumerate(f):
                if i < self.cur_line:
                    continue
                elif i > self.cur_line:
                    break

                self.cur_line += 1
                return line
        return None


# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class LorePlayerManager:

    players = {}
    data = {}
    saved_path = FILE_PATH + "data.json"

    def __init__(self):
        if not os.path.isfile(self.saved_path):
            os.makedirs(FILE_PATH + "active/")
            with open(self.saved_path, "w") as f:
                f.write("{}")
        with open(self.saved_path, "r") as json_file:
            self.data = json.load(json_file)

        for file in os.listdir(FILE_PATH + "active/"):
            if file.endswith(".txt"):
                snwflk = file.split(".", 1)[0]
                if snwflk not in (dt := self.data):
                    dt[snwflk] = 0
                self.players[snwflk] = LorePlayer(snwflk, dt[snwflk])

    async def replyIfMatch(self, msg):
        # await msg.channel.send(self.players)
        # await msg.channel.send(self.data)

        if (snwflk := str(msg.author.id)) in self.players:
            playr = self.players[snwflk]
            line = playr.readline(msg.content)

            if line:
                await msg.channel.send(f"{line} Anyways,")

            if self.data[snwflk] != (l := playr.get_cur_line()):
                self.data[snwflk] = l
                with open(self.saved_path, "w") as outfile:
                    json.dump(self.data, outfile)
