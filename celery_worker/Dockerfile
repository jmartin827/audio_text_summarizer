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

# Set the working directory to /app
WORKDIR /

# Copy the current directory contents into the container at /app
COPY . /

WORKDIR /app

# TODO determine the best strategy for running Whisper.
# threads prevents multiprocessing.
# --pool=solo is likely a single task per worker--it appears faster overall.


#CMD ["celery", "--app", "tasks.process", "worker", "--pool", "threads", "--loglevel=info"]

# This appears to be 30% faster for larger files when running on M1 cpu
CMD ["celery", "--app", "tasks.process", "worker", "--pool=solo", "--loglevel=info"]

# TODO test this as well:
# CMD ["celery", "--app", "tasks.process", "worker", "--pool=solo", "--loglevel=info", "--concurrency=1"]

