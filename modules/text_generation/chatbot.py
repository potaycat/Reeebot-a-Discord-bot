import asyncio
from random import random, choice

from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline
import torch


MODEL_PATH = "modules/text_generation/model/dialoGPT-medium-plain/"

class Talking:

    starter = pipeline(
        "text-generation",
        model="modules/text_generation/model/gpt2-wattpad-romance",
        tokenizer="gpt2",
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

    def __init__(self, ctx, instant_mode=False):
        self.ctx = ctx
        self.running = True
        self.is_instant = instant_mode
        self.pingable = ["you", "them"]

    async def run(self):
        tok = Talking.tokenizer
        chn = self.ctx.channel
        waiting = 0
        from_new_convo = 0
        last_output = ""
        say_something = False
        is_in_convo = self.is_instant
        init = self.is_instant
        while self.running:
            if init:
                async with self.ctx.typing():
                    pregenned = Talking.starter("", max_length=40)[0]['generated_text']
                    pregenned = pregenned.replace('P0', self.pingable[0])
                    if len(self.pingable) > 1:
                        pregenned = pregenned.replace('P1', self.pingable[1])
                await chn.send(pregenned)
                init = False
                is_in_convo = True
                from_new_convo = 2
                waiting = 60
                last_output = ""
                print("(new convo)")
            if say_something:
                async with self.ctx.typing():
                    chat_hist = []
                    async for msg in chn.history(limit=from_new_convo):
                        if len(msg.content) < 2:
                            continue
                        print(msg.content)
                        encoded = tok.encode(msg.content+tok.eos_token, return_tensors='pt')
                        chat_hist.insert(0, encoded)
                    while True:
                        bot_input_ids = torch.cat(chat_hist, dim=-1)
                        chat_history_ids = Talking.model.generate(bot_input_ids, max_length=1000, pad_token_id=tok.eos_token_id)
                        output_ = tok.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
                        if not output_ or last_output == output_:
                            print(output_)
                            output_ = choice(self.ctx.guild.emojis)
                            from_new_convo = 0
                            break
                        else:
                            break
                    last_output = output_
                    from_new_convo = from_new_convo if from_new_convo >=6 else from_new_convo+1
                await chn.send(output_)
                

            if is_in_convo:
                waiting -= 1
                await asyncio.sleep(20)
                async for msg in chn.history(limit=1):
                    if msg.author.bot:
                        print("(is bot)")
                        say_something = False
                    else:
                        print("(is user)")
                        say_something = True
                        waiting = 10
                if waiting < 1:
                    is_in_convo = False
                    print("(end convo)")
            elif self.is_instant:
                self.running = False
                await chn.send("Bye! I left the channel")
            else:
                await asyncio.sleep(600)
                if random() < 0.4:
                    init = True
                # await chn.send('`skip`')