FROM python:3.10.0-slim-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

RUN python -m pip install -r requirements.txt && \
    python -m spacy download en_core_web_sm && \
    python -m spacy link en_core_web_sm en

# Update and install git
RUN apt-get update && apt-get install -y git

# Install ffmpeg for whisper audio transcription
RUN apt-get install -y ffmpeg

# Install latest OpenAI whisper pip package
RUN python -m pip install git+https://github.com/openai/whisper.git

# VI and redis cli for testing/debug
RUN apt-get install -y vim
RUN apt-get install -y redis-server

# Set the working directory to /app
WORKDIR /

# Copy the current directory contents into the container at /app
COPY . /
WORKDIR /app

# Appears to be the most stable as Whisper can't support multithread and handles multicore automatically
# Disabling mingle as the initialization process can take some time
# Will not start the worker until it detects Redis is online
ENTRYPOINT sh -c 'until redis-cli -h redis -p 6379 ping; do sleep 4; done && celery --app tasks.process worker --pool=solo --loglevel=info --concurrency=1 --without-mingle'


