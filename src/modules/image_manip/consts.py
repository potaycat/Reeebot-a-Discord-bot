import os

FILE_PATH = "src/modules/image_manip/comvis/"
KALEIDO_API_KEY = os.getenv("KALEIDO_API_KEY")

DANK_SET = os.listdir(FILE_PATH + "emoji/dank/")
WHOLESOME_SET = os.listdir(FILE_PATH + "emoji/wholesome/")
