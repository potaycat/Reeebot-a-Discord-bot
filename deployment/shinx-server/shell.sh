#!/bin/sh

sudo apt update
sudo apt install -y ffmpeg libsm6 libxext6
sudo apt install -y git

mkdir -p src
git clone https://github.com/potaycat/Reeebot-a-Discord-bot src
#mv src/* ./
cp -rn ./data_bak ./src/data
cp env.prod ./src/.env
cd src
git fetch
git pull --rebase

python -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt

python main.py
