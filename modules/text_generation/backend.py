import typing as t


class Blenderbot1B:
    initialized = False

    def __init__(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        from transformers import set_seed

        name = "facebook/blenderbot-1B-distill"
        torch.set_grad_enabled(False)
        self.__class__.tokenizer = AutoTokenizer.from_pretrained(name)
        self.__class__.model = AutoModelForSeq2SeqLM.from_pretrained(name)
        self.__class__.generation_settings = {
            'min_new_tokens':24,
            'max_new_tokens':128,
        }
        self.__class__.name = name
        self.__class__.initialized = True

    @staticmethod
    def generate(prompt: str, gen_settings: t.Dict[str, t.Any]):
        input_ids = Blenderbot1B.tokenizer(prompt, return_tensors="pt")
        beam_output = Blenderbot1B.model.generate(
            **input_ids,
            **gen_settings,
        )
        out = Blenderbot1B.tokenizer.decode(beam_output[0], skip_special_tokens=True)
        return out.strip()


class BioGPT:
    initialized = False

    def __init__(self):
        import torch
        from transformers import BioGptTokenizer, BioGptForCausalLM

        name = "microsoft/biogpt"
        torch.set_grad_enabled(False)
        self.__class__.tokenizer = BioGptTokenizer.from_pretrained(name)
        self.__class__.model = BioGptForCausalLM.from_pretrained(name)
        self.__class__.generation_settings = {
            'min_new_tokens':24,
            'max_new_tokens':128,
            'early_stopping':True,
            'do_sample':False,
            'num_beams':2,
            'num_beam_groups':2,
            'temperature':0.9,
            'top_p':0.9,
            'top_k':0,
            'repetition_penalty':1.9,
        }
        self.__class__.name = name
        self.__class__.initialized = True

    @staticmethod
    def generate(prompt: str, gen_settings: t.Dict[str, t.Any]):
        input_ids = BioGPT.tokenizer(prompt, return_tensors="pt")
        beam_output = BioGPT.model.generate(
            **input_ids,
            **gen_settings,
        )
        out = BioGPT.tokenizer.decode(beam_output[0], skip_special_tokens=True)
        return out.strip()

 