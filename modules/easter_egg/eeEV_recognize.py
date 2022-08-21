from ..image_awareness.backend import ImageStore, ClassPredictor
from ..text_generation.backend import GPT2Wrapper


class eeAware:
    async def recognize(self, url):
        img = ImageStore()
        if not ClassPredictor.initialized:
            return ""
        await img.open_from_url(url)
        predicted = ClassPredictor.most_likely(
            img.image_, threshold=0.8, lower_threshold=0.7
        )
        # print(url)
        # print(pd)
        if predicted == "I don't know":
            return ""

        if not GPT2Wrapper.initialized:
            return f"Oh hey you {predicted}!"
        reply = GPT2Wrapper.gen(
            "distilgdex", f"Oh hey you {predicted}! I heard that {predicted}"
        )
        return reply + "\n"

    async def replyIfMatch(self, msg):
        if evDetected := await self.recognize(msg.author.avatar.url):
            await msg.channel.send(evDetected)
