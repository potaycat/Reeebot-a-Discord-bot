FROM python:3.8-slim-bullseye

RUN apt update && apt install -y \
    ffmpeg \
    libsm6 \
    libxext6

COPY .env .
COPY *.py .
COPY modules ./modules
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python"]
