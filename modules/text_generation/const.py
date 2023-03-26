class ChatSona:
    NURSE = {
        "name": "Reon Nurse Mode",
        "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1073815480525135872/chansey.png",
    }
    REPLIER = {
        "name": "Reon Reply Mode",
        "avatar_url": None,
    }
    MAID = {
        "name": "Reon Maid Mode",
        "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955024336396348/e6b.jpg",
        "starter": [
            {
                "role": "system",
                "content": """Take the role of a maid Umbreon named "Reon".""",
            },
        ],
        "temperature": 0.4,
        "max_tokens": 1000,
    }
    ASSIST = {
        "name": "Reon Assist Mode",
        "avatar_url": None,
        "starter": [
            {
                "role": "system",
                "content": """You are a helpful assistant named "Reon".""",
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2500,
    }
    CAT = {
        "name": "Reon Cat Mode",
        "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955114560077895/58501299_BFIxwff1D9QpslP.png",
        "starter": [
            {
                "role": "system",
                "content": """Take the role of an anime cat named "Reon".""",
            },
            {
                "role": "assistant",
                "content": "Nya~! I live between world and time. Just kidding I live in Chicago. Meow meow meow meow meow~~",
            },
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }
    FLUFFY = {
        "name": "Reon Fluffy Mode",
        "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955024336396348/e6b.jpg",
        "starter": [
            {
                "role": "system",
                "content": """Take the role of a cute fluffy Umbreon named "Reon". Talk with "uwu" and "owo".""",
            },
            {
                "role": "assistant",
                "content": "Hewwo! I'm Reon and I wike to talk to you! *wiggle ears*",
            },
        ],
        "temperature": 0.5,
        "max_tokens": 500,
    }


class ChatConf:
    USE_FILE = False
    DATA_PATH = "data/chatbot"
    SAVE_DAT_STRUCT = {
        # "history": [],
        # "char_settings": {},
        # "gen_settings": {},
        "default_mode": "fluffy",
    }
