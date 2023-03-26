from discord.ext import commands
from discord.app_commands import command, choices, Choice
from utils import arequests
from discord import File
from base64 import b64decode
from io import BytesIO
import os
from asyncio import sleep
from random import randint
from .help_msg import *


class ImageGen(commands.Cog, name="4. Image Generation"):
    BASE_URL = "https://api.runpod.ai/v1/kle30f6hbm4f5i"
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {os.getenv('RUN_POD_API_KEY')}",
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(fallback="kemono")
    @choices(
        sampling_method=[
            Choice(name=x, value=x)
            for x in [
                "Euler a",
                "Euler",
                "LMS",
                "Heun",
                "DPM2",
                "DPM2 a",
                "DPM++ 2S a",
                "DPM++ 2M",
                "DPM++ SDE",
                "DPM fast",
                "DPM adaptive",
                "LMS Karras",
                "DPM2 Karras",
                "DPM2 a Karras",
                "DPM++ 2S a Karras",
                "DPM++ 2M Karras",
                "DPM++ SDE Karras",
                "DDIM",
                "PLMS",
            ]
        ]
    )
    async def imagine(
        self,
        ctx,
        prompt,
        negative_prompt="(EasyNegative:1.0),(worst quality, low quality:1.4)",
        sampling_method: Choice[str] = None,
        steps: int = 20,
        cfg_scale: float = 7.5,
        seed: int = None,
    ):
        """
        Imagine a kemono furry
        """
        await ctx.interaction.response.defer()
        if not ctx.channel.is_nsfw():
            negative_prompt += ",nsfw,nude,naked,navel"
        input_ = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_index": "DPM++ 2M Karras"
            if sampling_method == None
            else sampling_method.value,
            "seed": seed or randint(1, 999999999),
        }
        body = {"input": input_}
        x = await arequests("POST", self.BASE_URL + "/run", self.HEADERS, body)
        if x.ok:
            id_ = x.json()["id"]
            while 1:
                x = await arequests(
                    "GET", self.BASE_URL + "/status/" + id_, self.HEADERS
                )
                if x.ok:
                    x = x.json()
                    if x["status"] == "COMPLETED":
                        break
                    else:
                        await sleep(0.2)
                else:
                    raise Exception(f"HTTP error: {x.status_code}. Job ID: {id_}")
        else:
            raise Exception(f"HTTP error: {x.status_code}")
        r = await ctx.reply(
            file=File(
                BytesIO(b64decode(x["output"]["images"][0])),
                filename="generated.png",
            )
        )
        try:
            await self.monitor(ctx, x, r)
        except Exception as e:
            await self.bot.low_log_channel.send(f"```{e}```<{ctx.message.jump_url}>")

    async def monitor(self, ctx, res, reply):
        info = {
            k: res["output"]["parameters"][k]
            for k in [
                "prompt",
                "negative_prompt",
                "steps",
                "sampler_index",
                "cfg_scale",
                "seed",
            ]
        }
        d_ = {
            "user": f"{ctx.author} ({ctx.author.id})",
            "command": "imagine kemono",
            "revision": "230327",
            "input": str(info)[:1500],
            "output": "<" + reply.attachments[0].url + ">",
        }
        await self.bot.low_log_channel.send(d_)

    @imagine.command()
    @choices(model=[Choice(name="Kemono", value="kemono")])
    async def info(self, ctx, model, eph=True):
        """
        Model info
        """
        match model:
            case "kemono":
                help_msg = KEM_HELP
            case _:
                help_msg = "kemono, "
        if ctx.interaction:
            await ctx.interaction.response.send_message(help_msg, ephemeral=eph)
        else:
            await ctx.send(help_msg)


async def setup(bot):
    await bot.add_cog(ImageGen(bot))
