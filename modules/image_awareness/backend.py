import os
import cv2
import numpy as np
from tensorflow import keras
# import matplotlib.pyplot as plt
from utils import ImageOpener


PATH = "modules/image_awareness/"
KERAS_MODEL = "EV-classify-1605309902.keras"
INPUT_SIZE = 299


class ClassPredictor(ImageOpener):
    initialized = False

    def __init__(self):
        ClassPredictor.SIZE_X = INPUT_SIZE
        ClassPredictor.SIZE_Y = INPUT_SIZE
        ClassPredictor._model = keras.models.load_model(os.path.join(PATH, KERAS_MODEL))
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

    def predict(self):
        self._image = cv2.cvtColor(self._image, cv2.COLOR_BGR2RGB) # BRUH
        # imgplot = plt.imshow(self.get_img())
        # plt.show()
        input_ = np.asarray([self.get_img()])
        pd = ClassPredictor._model.predict(input_)[0]
        return pd

    def most_likely(self, pd, threshold = 0.6):
        dom = np.argmax(pd)
        if pd[dom] < threshold:
            return "I don't know"
        predicted = ClassPredictor.labels[dom]
        return predicted
        