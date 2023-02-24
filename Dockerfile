# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Create venv
#RUN python -m venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

#RUN #. /opt/venv/bin/activate
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
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "app.src.main:app", "--host", "0.0.0.0", "--port", "80"]
