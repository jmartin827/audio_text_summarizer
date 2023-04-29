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

# VI and redis cli for testing/debug
RUN apt-get install -y vim
RUN apt-get install -y redis-server

# Copy the current directory contents into the container at /app
COPY . /
WORKDIR /worker

# Green threaded to handle cocurrent requests. Mingle appears to slow down initialization.
# TODO have an iniitalization which sends a test job to the endpoint in case the model is not preloaded.
ENTRYPOINT sh -c 'until redis-cli -h redis -p 6379 ping; do sleep 4; done && celery --app tasks.process worker --pool=gevent --concurrency=200 --loglevel=info --without-mingle'


