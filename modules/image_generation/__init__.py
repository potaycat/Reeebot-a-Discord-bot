from discord.ext import commands


class ImageAware(commands.Cog, name="4. Image Awareness"):
    # @commands.hybrid_group(invoke_without_command=True, fallback="lucario")
    async def imagine(
        self, ctx
    ):
        """
        Imagine a lucario
        """
        x = ImageFilterer()
        await x.load_from_msg(ctx.message, avatar, upload or img_link)
        await x.deepfry()
        x = await x.export_png(
            f"{ctx.message.author}{ctx.message.created_at.timestamp()}"
        )
        await ctx.send(file=File(x))


        async def monitor():
            res = json.loads(str(res))
            res["choices"][0]["message"]["content"] = res["choices"][0]["message"][
                "content"
            ][:200]
            d_ = {
                "asker": f"{ctx.author} ({ctx.author.id})",
                "msg_url": "<" + ctx.message.jump_url + ">",
                '"mode"': str(mode),
                "revision": "230317",
                "question": message[:200],
                "response": str(res),
            }
            await self.bot.low_log_channel.send(d_)

        await monitor()


async def setup(bot):
    await bot.add_cog(ImageAware(bot))
