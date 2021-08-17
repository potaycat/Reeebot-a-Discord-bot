from ..image_awareness.backend import ClassPredictor
from ..text_generation.backend import GPT2Wrapper


class eeAware():
    
    def recognize(self, url):
        if ClassPredictor.initialized:
            return ""
        ClassPredictor.open_from_url(url)
        pd = ClassPredictor.predict()
        # print(url)
        # print(pd)
        if (predicted:=ClassPredictor.most_likely(pd, threshold = 0.8))\
            [0] == "I":
            return ""

        if not GPT2Wrapper.initialized:
            return (f'Oh hey you {predicted}!')
        reply = GPT2Wrapper.gen('distilgdex', f'Oh hey you {predicted}! I heard that {predicted}')
        return reply + '\n'