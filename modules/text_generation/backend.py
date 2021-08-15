from transformers import pipeline, set_seed
from random import randint 


class GPT2Wrapper:
    initialized = False
    
    def __init__(self):
        seed = randint(0, 9999)
        set_seed(seed)
        print(seed)

        GPT2Wrapper._pipeline = pipeline(
            "text-generation",
            model="modules/text_generation/model/bwurtz-gpt2-med-2203-adam-b16/checkpoint-1536/",
            tokenizer="distilgpt2",
        )
        GPT2Wrapper._pipeline2 = pipeline(
            "text-generation",
            model="modules/text_generation/model/bwurtz-gpt2-med-2203-adam-b16/checkpoint-1536/",
            tokenizer="distilgpt2",
        )
        GPT2Wrapper.initialized = True


    def gen(self, str_=""):
        text = GPT2Wrapper._pipeline(str_, max_length=30)
        text = text[0]["generated_text"]
        text = text.strip()
        try:
            last_period = text.rindex(".")
            text = text[0 : last_period + 1]
        except:
            pass
        return text
