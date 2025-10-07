FROM python:3.10-slim-bullseye

RUN apt update
RUN apt install -y ffmpeg libsm6 libxext6 git
RUN pip install --upgrade pip

RUN git clone https://github.com/potaycat/Reeebot-a-Discord-bot /src
WORKDIR src
RUN pip install -r requirements.txt
COPY .env .
COPY data ./data

# RUN python tests.py

CMD ["python"]
