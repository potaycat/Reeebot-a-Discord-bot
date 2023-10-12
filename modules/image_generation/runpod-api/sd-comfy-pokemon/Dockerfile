from runpod/pytorch:3.10-2.0.1-118-runtime

RUN apt update
RUN apt install -y git wget
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR "ComfyUI"
RUN pip install -r requirements.txt
RUN wget https://civitai.com/api/download/models/156883 -O ./models/checkpoints/yiffymix_v34.safetensors
RUN wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15s2_lineart_anime.pth -O ./models/controlnet/control_v11p_sd15s2_lineart_anime.pth
RUN wget -O ./models/vae/kl-f8-anime2.vae.safetensors "https://civitai.com/api/download/models/156883?type=VAE&format=Other" --content-disposition
RUN wget https://civitai.com/api/download/models/153453 -O ./models/loras/FurryCoreV2New-07.safetensors
RUN wget https://civitai.com/api/download/models/132413 -O ./models/loras/Y1-Furry-Eeveelution.safetensors

RUN wget https://civitai.com/api/download/models/16734 -O ./models/loras/LucarioV1.safetensors
RUN wget https://civitai.com/api/download/models/94047 -O ./models/loras/litten-08.safetensors
RUN wget https://civitai.com/api/download/models/133144 -O ./models/loras/floragato-v1-locon.safetensors
RUN wget https://civitai.com/api/download/models/97473 -O ./models/loras/Umbreon_LoRA_V2.safetensors

WORKDIR /
RUN apt remove -y git wget
RUN pip install runpod
ADD handler.py .
CMD [ "python", "-u", "/handler.py" ]
