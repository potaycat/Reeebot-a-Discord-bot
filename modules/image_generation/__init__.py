from discord.ext import commands
from discord import app_commands
from utils import arequests
from discord import File, Attachment
from base64 import b64decode
from io import BytesIO
import os
import asyncio
from random import randint
import discord
import json


class ImageGen(commands.Cog, name="4. Image Generation"):
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {os.getenv('RUN_POD_API_KEY')}",
    }
    with open(
        "./modules/image_generation/runpod-api/sd-comfy-pokemon/workflow_api.json",
        "r",
    ) as f:
        COMFY_PROMPT = f.read()

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(fallback="kemono")
    @app_commands.choices(
        sampling_method=[
            app_commands.Choice(name=x, value=x)
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
        sampling_method: app_commands.Choice[str] = None,
        steps: app_commands.Range[int, 1, 200] = None,
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
                ctx,
                str(u_in)[:1500],
                x["id"],
                up.attachments[0].url,
                "imagine kemono",
                "230404",
            )
        except Exception as e:
            await self.bot.low_log_channel.send(f"```{e}```<{ctx.message.jump_url}>")

    @commands.hybrid_group(fallback="pokemon")
    @app_commands.choices(
        spiecies=[
            app_commands.Choice(name="Lucario", value="LucarioV1.safetensors"),
            app_commands.Choice(name="Litten", value="litten-08.safetensors"),
            app_commands.Choice(
                name="Floragato", value="floragato-v1-locon.safetensors"
            ),
            app_commands.Choice(name="Umbreon", value="Umbreon_LoRA_V2.safetensors"),
        ]
    )
    async def colorize(
        self,
        ctx,
        sketch: Attachment,
        spiecies: app_commands.Choice[str],
        prompt="",
        dark=False,
        negative_prompt="",
        auto_prompt=True,
        seed: int = None,
    ):
        """
        Colorize a Pokemon sketch
        """
        await ctx.interaction.response.defer()
        img_name = sketch.url.split("/")[-1].split("?")[0]
        seed = seed or randint(1, 999999999999999)
        if auto_prompt:
            if prompt:
                prompt = ", " + prompt
            if negative_prompt:
                negative_prompt = ", " + negative_prompt
            prompt = f"{spiecies.name.lower()}, feral, pokemon, cute{prompt}"
            negative_prompt = f"low quality, bad anatomy, deformity{negative_prompt}"

        json_text = self.COMFY_PROMPT
        json_text = ( # replace 1st occurrence
            json_text.replace("<STR IMAGE FILE>", img_name, 1)
            .replace('"<INT SEED>"', str(seed), 1)
            .replace('"<INT LATENT BATCH>"', "4", 1)
            .replace("<STR NEGATIVE>", negative_prompt, 1)
            .replace("<STR POSITIVE>", prompt, 1)
            .replace("<STR LORA NAME>", spiecies.value, 1)
            .replace("<VAEEncode input ind>", "25" if dark else "21", 1)
        )
        input_ = json.loads(json_text)
        input_["img_url"] = sketch.url
        body = {"input": input_}
        x = await self.runpod("https://api.runpod.ai/v2/69xjmjth10zw7e", body)
        up_img = [
            File(BytesIO(b64decode(img[2:])), filename=f"{i}.png")
            for i, img in enumerate(x["output"]["outputs"])
        ]
        up = await self.bot.img_dump_chnl.send(files=up_img)
        btn = ImgButtons()
        r = await ctx.reply(
            f"Colored from sketch: [link]({sketch.url})",
            embeds=[
                discord.Embed(url="https://umbrecore.com/?r=d_e").set_image(
                    url=attch.url
                )
                for attch in up.attachments
            ],
            view=btn,
        )
        btn.res_msg = r
        btn.del_btn_hanldr = (self.delete_generation, x["id"])
        """ Log to channel """
        try:
            u_in = {
                "sketch": sketch.url,
                "spiecies": spiecies.name,
                "prompt": prompt,
                "dark_latent": dark,
                "negative_prompt": negative_prompt,
                "seed": seed,
            }
            await self.log(
                ctx, u_in, x["id"], up.jump_url, "colorize pokemon", "231012"
            )
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
            "output": "<" + up + ">",
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
            print(id_)
            while 1:
                x = await arequests("GET", url + "/status/" + id_, self.HEADERS)
                if x.ok:
                    x = x.json()
                    if x["status"] == "COMPLETED":
                        break
                    elif x["status"] == "FAILED":
                        raise Exception(f"Runpod failure. Job ID: {id_}")
                    else:
                        await asyncio.sleep(0.2)
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
