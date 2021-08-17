from ..image_awareness.backend import ImageStore, ClassPredictor
from ..text_generation.backend import GPT2Wrapper


class eeAware():
    
    def recognize(self, url):
        img = ImageStore()
        if not ClassPredictor.initialized:
            return ""
        img.open_from_url(url)
        predicted = ClassPredictor.most_likely(img.get_img(), threshold=0.8, lower_threshold=0.7)
        # print(url)
        # print(pd)
        if predicted[0] == "I":
            return ""

        if not GPT2Wrapper.initialized:
            return (f'Oh hey you {predicted}!')
        reply = GPT2Wrapper.gen('distilgdex', f'Oh hey you {predicted}! I heard that {predicted}')
        return reply + '\n'