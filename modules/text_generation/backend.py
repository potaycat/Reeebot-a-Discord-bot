from random import randint 


class GPT2Wrapper:
    initialized = False
    
    def __init__(self):
        from transformers import pipeline, set_seed

        seed = randint(0, 9999)
        set_seed(seed)
        print(seed)

        GPT2Wrapper.distilgdex = pipeline(
            "text-generation",
            model="modules/text_generation/model/distilgdex",
            tokenizer="distilgpt2",
        )
        GPT2Wrapper.crappost = pipeline(
            "text-generation",
            model="modules/text_generation/model/bwurtz-gpt2-med-2203-adam-b16/checkpoint-1536/",
            tokenizer="distilgpt2",
        )
        GPT2Wrapper.initialized = True

    @staticmethod
    def gen(pipeline='distilgdex', prompt="", **kwargs):
        gen_pipeline = getattr(foo, pipeline)
        text = gen_pipeline(prompt, max_length=kwargs['max_length'])
        text = text[0]["generated_text"]
        text = text.strip()
        try:
            last_period = text.rindex(".")
            text = text[0 : last_period + 1]
        except:
            pass
        return text
