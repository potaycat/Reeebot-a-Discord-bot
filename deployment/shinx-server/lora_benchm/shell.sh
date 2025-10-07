#!/bin/sh


python -m venv venv
. venv/bin/activate
pip install --upgrade pip

pip install gdown
gdown -O LucarioLoRA.safetensors https://drive.google.com/uc?id=1BrwBns8ktDh2J24XZmPppJwitigbZJ_N

pip install transformers accelerate xformer diffusers==0.14.0 safetensors
git clone https://github.com/kohya-ss/sd-scripts.git sdscripts


python benchm.py
