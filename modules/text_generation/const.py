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
    }
    ASSIST = {
        "name": "Reon Assist Mode",
        "avatar_url": None,
    }
    CAT = {
        "name": "Reon Cat Mode",
        "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955114560077895/58501299_BFIxwff1D9QpslP.png",
    }
    FLUFFY = {
        "name": "Reon Fluffy Mode",
        "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955024336396348/e6b.jpg",
    }


class ChatConf:
    USE_FILE = True
    DATA_PATH = "data/chatbot"
    SAVE_DAT_STRUCT = {
        # "history": [],
        # "char_settings": {},
        # "gen_settings": {},
        "blenderb_history": [],
        "blenderb_gen_settings": {},
        "biogpt_gen_settings": {},
    }
