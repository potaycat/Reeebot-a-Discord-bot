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
import aiohttp
from typing import Optional


class ImageGen(commands.Cog, name="4. Image Generation"):

    def __init__(self, bot):
        self.HEADERS = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {os.getenv('RUN_POD_API_KEY')}",
        }
        with open(
            "src/modules/image_generation/runpod-api/comfyui-noobai-wf.json",
            "r",
        ) as f:
            self.comfyuinoobaiwf = f.read()
        self.session = aiohttp.ClientSession()
        self.bot = bot

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    @commands.hybrid_command()
    @app_commands.choices(
        output_count=[
            app_commands.Choice(name=x, value=x)
            for x in [
                "1",
                "2",
                "4",
                "6",
                "9",
            ]
        ]
    )
    async def imagine(
        self,
        ctx,
        prompt,
        negative_prompt: str = "",
        output_count: app_commands.Choice[str] = None,
        seed: int = None,
    ):
        """
        Uses NoobAI for image generation.
        """
        asyncio.create_task(ctx.interaction.response.defer())
        seed = seed if seed else randint(1, 999999999999999)
        output_count = output_count.value if output_count else "2"
        json_text = self.comfyuinoobaiwf
        json_text = (  # replace 1st occurrence
            json_text.replace("<INT SEED>", str(seed), 1)
            .replace("<INT OUTPUT_NUM>", output_count, 1)
            .replace("<STR NEGATIVE>", negative_prompt, 1)
            .replace("<STR POSITIVE>", prompt, 1)
        )
        input_ = json.loads(json_text)
        body = {"input": {"workflow": input_}}
        x = await self.runpod("https://api.runpod.ai/v2/bauvaojuoja55e", body)
        file_list = [
            File(BytesIO(b64decode(img["data"])), filename="generated.png")
            for img in x["output"]["images"]
        ]
        up = await self.bot.img_dump_chnl.send(files=file_list)
        images = [attch.url for attch in up.attachments]
        btn = ImgButtons()
        # Send all image URLs in one message
        r = await ctx.reply(" ".join(images), view=btn)
        btn.res_msg = r
        btn.del_btn_hanldr = (self.delete_generation, x["id"])

        u_in = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "output_count": output_count,
            "seed": seed,
        }
        x["output"] = {}
        await self.log(
            ctx,
            str(u_in)[:1500],
            x,
            up.jump_url,
            "imagine",
            "251008",
        )

    @commands.hybrid_command()
    async def nano_banana(
        self,
        ctx,
        prompt: str,
        input1: Attachment,
        input2: Optional[Attachment] = None,
        input3: Optional[Attachment] = None,
        input4: Optional[Attachment] = None,
    ):
        """Edit images using nano-banana."""
        asyncio.create_task(ctx.interaction.response.defer())

        # Collect all provided image URLs
        images = [input1.url]
        for img in [input2, input3, input4]:
            if img:
                images.append(img.url)

        try:
            body = {
                "input": {
                    "prompt": prompt,
                    "images": images,
                    "enable_safety_checker": True,
                }
            }
            x = await self.runpod("https://api.runpod.ai/v2/nano-banana-edit", body)

            # Download the result image
            async with self.session.get(x["output"]["result"]) as resp:
                if resp.status == 200:
                    img_data = await resp.read()
                else:
                    raise Exception(f"Failed to download result image: {resp.status}")
            up = await self.bot.img_dump_chnl.send(
                file=File(BytesIO(img_data), filename="edited.png")
            )

            btn = ImgButtons()
            r = await ctx.reply(up.attachments[0].url)
            btn.res_msg = r
            btn.del_btn_hanldr = (self.delete_generation, x["id"])

            del x["output"]["result"]
            await self.log(
                ctx,
                str({"prompt": prompt, "image_count": len(images)}),
                x,
                up.jump_url,
                "nano_banana",
                "251008",
            )
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

    async def log(self, ctx, input_, id_, up, command, revision):
        d_ = {
            "user": f"{ctx.author} ({ctx.author.id})",
            "msg_url": "<" + ctx.message.jump_url + ">",
            "command": command,
            "revision": revision,
            "input": input_,
            "job_detail": id_,
            "output": "<" + up + ">",
        }
        try:
            await self.bot.low_log_channel.send(d_)
        except:
            pass

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
        async with self.session.post(
            url + "/run", headers=self.HEADERS, json=body
        ) as response:
            if response.status == 200:
                data = await response.json()
                id_ = data["id"]
                # print(id_)
                while True:
                    async with self.session.get(
                        url + "/status/" + id_, headers=self.HEADERS
                    ) as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            if status_data["status"] == "COMPLETED":
                                return status_data
                            elif status_data["status"] == "FAILED":
                                raise Exception(
                                    f"Runpod failure. Detail: {status_data}"
                                )
                            else:
                                await asyncio.sleep(0.1)
                        else:
                            raise Exception(
                                f"HTTP error: {status_response.status}. Job ID: {id_}"
                            )
            else:
                raise Exception(f"HTTP error: {response.status}")


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
