from discord.ext import commands
from discord.app_commands import command, choices, Choice
from utils import arequests
from discord import File
from base64 import b64decode
from io import BytesIO
import os
import asyncio
from random import randint
from .help_msg import *
import discord


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
        try_prevent_nsfw: bool,
        easy_negative=True,
        negative_prompt: str = "",
        sampling_method: Choice[str] = None,
        steps: int = None,
        cfg_scale: float = None,
        seed: int = None,
    ):
        """
        Imagine a kemono furry
        """
        asyncio.create_task(ctx.interaction.response.defer())
        np = negative_prompt
        if easy_negative:
            if np:
                np += ","
            np += "(boring_e621:1.0),(EasyNegative:0.8),(deformityv6:0.8),(bad-image-v2:0.8),(worst quality, low quality:1.4),bad anatomy, bad hands, error, extra digit, fewer digits."
        if try_prevent_nsfw:
            if np:
                np += ","
            np += "nsfw,nude,naked,navel,genital"
        input_ = {
            "prompt": prompt,
            "negative_prompt": np,
            "steps": steps or 20,
            "cfg_scale": cfg_scale or 7.5,
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
                        await asyncio.sleep(0.1)
                else:
                    raise Exception(f"HTTP error: {x.status_code}. Job ID: {id_}")
        else:
            raise Exception(f"HTTP error: {x.status_code}")
        up = await self.bot.img_dump_chnl.send(
            file=File(
                BytesIO(b64decode(x["output"]["images"][0])),
                filename="generated.png",
            )
        )
        btn = ImgButtons()
        r = await ctx.reply(up.attachments[0].url, view=btn)
        btn.res_msg = r
        btn.del_btn_hanldr = (self.delete_generation, id_)

        """ Log to channel """
        try:
            ks = ["seed"]
            if negative_prompt:
                ks.append("negative_prompt")
            if sampling_method:
                ks.append("sampler_index")
            if steps:
                ks.append("steps")
            if cfg_scale:
                ks.append("cfg_scale")
            u_in = {k: x["output"]["parameters"][k] for k in ks}
            if sampling_method:
                u_in["sampling_method"] = u_in.pop("sampler_index")
            u_in["try_prevent_nsfw"] = try_prevent_nsfw
            u_in["easy_negative"] = easy_negative
            d_ = {
                "user": f"{ctx.author} ({ctx.author.id})",
                "command": "imagine kemono",
                "revision": "230402",
                "input": str(u_in)[:1500],
                "job_id": id_,
                "output": "<" + up.attachments[0].url + ">",
            }
            await self.bot.low_log_channel.send(d_)
        except Exception as e:
            await self.bot.low_log_channel.send(f"```{e}```<{ctx.message.jump_url}>")

    async def delete_generation(self, msg, interaction, jid, reason=None):
        await msg.delete()
        d_ = {
            "actor": f"{interaction.user} ({interaction.user.id})",
            "job_id": jid,
            "action": "delete",
            "reason": reason,
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


class ImgButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Delete",
        style=discord.ButtonStyle.gray,
    )
    async def delete(self, interaction, button):
        delete_generation, id_ = self.del_btn_hanldr
        await delete_generation(self.res_msg, interaction, id_)

    async def on_timeout(self):
        await self.res_msg.edit(view=None)


async def setup(bot):
    await bot.add_cog(ImageGen(bot))
