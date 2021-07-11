FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libsodium-dev \
    libffi-dev \
    libnacl-dev \
    python3-dev \
    ffmpeg \
    && python3 -m pip install -U discord.py[voice] \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "-u", "toru.py"]
