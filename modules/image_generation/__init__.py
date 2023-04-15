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
        x = await self.runpod("https://api.runpod.ai/v2/kle30f6hbm4f5i", body)
        up = await self.bot.img_dump_chnl.send(
            file=File(
                BytesIO(b64decode(x["output"]["images"][0])),
                filename="generated.png",
            )
        )
        btn = ImgButtons()
        r = await ctx.reply(up.attachments[0].url, view=btn)
        btn.res_msg = r
        btn.del_btn_hanldr = (self.delete_generation, x["id"])
        """ Log to channel """
        try:
            ks = ["prompt", "seed"]
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
            await self.log(
                ctx, str(u_in)[:1500], x["id"], up, "imagine kemono", "230404"
            )
        except Exception as e:
            await self.bot.low_log_channel.send(f"```{e}```<{ctx.message.jump_url}>")

    @imagine.command()
    @choices(
        spiecies=[
            Choice(name="Lucario", value="LucarioLoRA.safetensors"),
            Choice(name="Meowscarada", value="MeowscaradaLoRA.safetensors"),
            Choice(name="Braixen", value="BraixenLoRA.safetensors"),
        ]
    )
    async def pokemon(
        self,
        ctx,
        spiecies: Choice[str],
        prompt,
        lora_weight: float = None,
        safety_check=True,
        easy_negative=True,
        negative_prompt: str = "",
        steps: int = None,
        cfg_scale: float = None,
        seed: int = None,
    ):
        """
        Imagine a Pokemon
        """
        asyncio.create_task(ctx.interaction.response.defer())
        np = negative_prompt
        if easy_negative:
            if np:
                np += ","
            np += "easynegative, bad_prompt, normal quality, bad quality"
        input_ = {
            "lora": spiecies.value,
            "lora_weight": lora_weight or 0.8,
            "prompt": f"{spiecies.name.lower()}, {prompt}",
            "negative_prompt": np,
            "steps": steps or 70,
            "cfg_scale": cfg_scale or 7.0,
            "seed": seed or randint(1, 999999999),
            "safety_check": safety_check,
        }
        body = {"input": input_}
        x = await self.runpod("https://api.runpod.ai/v2/ebuz1knogyus6p", body)
        up = await self.bot.img_dump_chnl.send(
            file=File(
                BytesIO(b64decode(x["output"]["output"])),
                filename="generated.png",
            )
        )
        btn = ImgButtons()
        r = await ctx.reply(up.attachments[0].url, view=btn)
        btn.res_msg = r
        btn.del_btn_hanldr = (self.delete_generation, x["id"])
        """ Log to channel """
        try:
            ks = ["lora", "prompt", "seed"]
            if negative_prompt:
                ks.append("negative_prompt")
            if steps:
                ks.append("steps")
            if cfg_scale:
                ks.append("cfg_scale")
            if lora_weight:
                ks.append("lora_weight")
            u_in = {k: x["output"]["input"][k] for k in ks}
            u_in["easy_negative"] = easy_negative
            u_in["nsfw_detected"] = x["output"]["nsfw_content_detected"]
            await self.log(ctx, u_in, x["id"], up, "imagine pokemon", "230415")
        except Exception as e:
            await self.bot.low_log_channel.send(f"```{e}```<{ctx.message.jump_url}>")

    async def log(self, ctx, input_, id_, up, command, revision):
        d_ = {
            "user": f"{ctx.author} ({ctx.author.id})",
            "msg_url": "<" + ctx.message.jump_url + ">",
            "command": command,
            "revision": revision,
            "input": input_,
            "job_id": id_,
            "output": "<" + up.attachments[0].url + ">",
        }
        await self.bot.low_log_channel.send(d_)

    async def delete_generation(self, msg, interaction, jid, reason=None):
        await msg.delete()
        d_ = {
            "actor": f"{interaction.user} ({interaction.user.id})",
            "job_id": jid,
            "action": "delete",
            "reason": reason,
        }
        await self.bot.low_log_channel.send(d_)

    async def runpod(self, url, body):
        x = await arequests("POST", url + "/run", self.HEADERS, body)
        if x.ok:
            id_ = x.json()["id"]
            while 1:
                x = await arequests("GET", url + "/status/" + id_, self.HEADERS)
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
        return x


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
