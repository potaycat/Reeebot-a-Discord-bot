import cv2
import numpy as np
from utils import ImageOpener


class ImageStore(ImageOpener):

    def __init__(self):
        self.SIZE_X = self.SIZE_Y = ClassPredictor.INPUT_SIZE


class ClassPredictor():
    initialized = False

    def __init__(self):
        if ClassPredictor.initialized:
            return
        import tflite_runtime.interpreter as tflite
        ClassPredictor.INPUT_SIZE = 299
        ClassPredictor._model = tflite.Interpreter(model_path='modules/image_awareness/EV-classify-1605309902.tflite')
        ClassPredictor._model.allocate_tensors()
        ClassPredictor.labels = [
            "Eevee",
            "Espeon",
            "Flareon",
            "Glaceon",
            "Jolteon",
            "Leafeon",
            "Sylveon",
            "Umbreon",
            "Vaporeon"
        ]
        ClassPredictor.initialized = True

    @staticmethod
    def predict(img):
        # cv2.imshow('img', img)
        # cv2.waitKey(0)

        input_ = np.asarray([img]).astype(np.float32)
        x = ClassPredictor._model
        x.set_tensor(0, input_)
        x.invoke()
        output_data = x.get_tensor(182)[0]
        return output_data

    @staticmethod
    def most_likely(img, threshold=0.6, lower_threshold=0.7):
        pd = ClassPredictor.predict(img).tolist()
        high_label_ind = np.argmax(pd)
        label_percentg = pd.pop(high_label_ind)
        if label_percentg < threshold and max(pd)>lower_threshold:
            return "I don't know"
        predicted = ClassPredictor.labels[high_label_ind]
        return predicted
        