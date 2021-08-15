import os
import json
import re
from random import choice

FILE_PATH = "modules/easter_egg/ee_lores/"


class LorePlayer():
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

    def get_last_int(line):
        # last number in string minus 1
        return int(re.findall(r'\d+', line)[-1]) - 1

    def readline(self, ip):
        with open(self.file_path) as f:
            for i, line in enumerate(f):
                # try:
                #     print("i:        "+str(i))
                #     print("self.cur: "+str(self.cur_line))
                #     print("input:    " + ip)
                #     print("cur line: "+line)
                #     print("------------------")
                # except:
                #     pass

                if i < self.cur_line:
                    continue
                elif i > self.cur_line:
                    break
                elif (sgnl := line[0]) == '#':
                    self.cur_line += 1
                    continue
                elif sgnl == '?':
                    if ip[2:] == line.split(' ')[1]:
                        self.cur_line = DialogPlayer.get_last_int(line)
                        continue
                    else:
                        self.cur_line += 1
                        continue
                elif sgnl == '}':
                    self.cur_line = DialogPlayer.get_last_int(line)
                    continue

                self.cur_line += 1
                return line
        return None


# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class LorePlayerManager():

    players = {}
    data = {}

    def __init__(self):
        with open(FILE_PATH+'data.json', 'r+') as json_file:
            self.data = json.load(json_file)

        for file in os.listdir(FILE_PATH+"active/"):
            if file.endswith(".txt"):
                snwflk = file.split('.', 1)[0]
                if snwflk not in (dt := self.data):
                    dt[snwflk] = 0
                self.players[snwflk] = DialogPlayer(snwflk, dt[snwflk])

    async def replyIfMatch(self, msg):
        # await msg.channel.send(self.players)
        # await msg.channel.send(self.data)

        if (snwflk := str(msg.author.id)) in self.players:
            playr = self.players[snwflk]
            line = playr.readline(msg.content)

            if line:
                await msg.channel.send(f"{line}{choice(['Anyways','Also','By the way','Oh and','Um..'])},")

            if self.data[snwflk] != (l := playr.get_cur_line()):
                self.data[snwflk] = l
                with open(FILE_PATH+'data.json', 'w') as outfile:
                    json.dump(self.data, outfile)
