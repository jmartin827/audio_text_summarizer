# Use an official Python runtime as a parent image
FROM python:3.10.0-slim-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# VI for basic debugging
RUN apt-get update && apt-get install -y vim

# Set the working directory to /app
WORKDIR /

# Copy the current directory contents into the container at /app
COPY . /

# Expose port 8000 for the API
EXPOSE 8000

# Start the API with Uvicorn. Root path set by default to "/" and reflected in ingress.yaml
CMD ["uvicorn", "app.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
