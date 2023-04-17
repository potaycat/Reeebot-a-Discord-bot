from python:3.10-buster

WORKDIR /

RUN pip install runpod transformers accelerate diffusers safetensors

RUN pip install gdown
RUN gdown -O LucarioLoRA.safetensors https://drive.google.com/uc?id=1BrwBns8ktDh2J24XZmPppJwitigbZJ_N
RUN gdown -O MeowscaradaLoRA.safetensors https://drive.google.com/uc?id=1UmeMypK6Az6J8nUyIWRQ-51uCCoBli2J
RUN gdown -O BraixenLoRA.safetensors https://drive.google.com/uc?id=1tlVQNg9eY8kqN0tRH3EjLS4uubnyRcv0

RUN gdown -O Crosskemono2.vae.pt https://drive.google.com/uc?id=1593rnwnKn-d34mNck2emUS111FTWRtrW
RUN wget -q https://raw.githubusercontent.com/huggingface/diffusers/main/scripts/convert_vae_pt_to_diffusers.py
RUN pip install omegaconf pytorch_lightning
RUN mkdir crosskemono2VAE
RUN python convert_vae_pt_to_diffusers.py --vae_pt_path Crosskemono2.vae.pt --dump_path crosskemono2VAE
RUN rm Crosskemono2.vae.pt

RUN pip uninstall omegaconf pytorch_lightning gdown

ADD cache_models.py .
RUN python cache_models.py

ADD handler.py .
CMD [ "python", "-u", "/handler.py" ]