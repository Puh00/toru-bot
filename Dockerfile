FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libsodium-dev
RUN python3 -m pip install -U discord.py[voice]
RUN apt install -y libffi-dev libnacl-dev python3-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y ffmpeg

CMD ["python", "-u", "toru.py"]
