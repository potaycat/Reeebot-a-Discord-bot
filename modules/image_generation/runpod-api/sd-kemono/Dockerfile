FROM runpod/stable-diffusion:web-automatic-base-4.0.0

SHELL ["/bin/bash", "-c"]

ENV PATH="${PATH}:/workspace/stable-diffusion-webui/venv/bin"
ENV MODELS=/workspace/stable-diffusion-webui/models

WORKDIR /

RUN pip install -U xformers
RUN pip install runpod

RUN rm $MODELS/Stable-diffusion/*
RUN mkdir $MODELS/Lora
# RUN wget -O $MODELS/Stable-diffusion/anything-v4.5-pruned.safetensors \
#     https://huggingface.co/andite/anything-v4.0/resolve/main/anything-v4.5-pruned.safetensors
# RUN wget -O $MODELS/Lora/Lucario.safetensors \
#     https://civitai.com/api/download/models/16734
RUN wget -O $MODELS/Stable-diffusion/Kemono.safetensors \
    https://civitai.com/api/download/models/32830

ADD handler.py .
ADD start.sh /start.sh
RUN chmod +x /start.sh

CMD [ "/start.sh" ]
