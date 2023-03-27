# Audio to Text Summarizer

This project allows users to upload an audio file and receive a summarized transcript via FastApi, 
along with a UUID that references the job status and provides access to the result. 

Fast API sends a task to Redis, which serves as a message broker, 
and a Celery worker retrieves the task from the queue using the UUID to identify the corresponding file.
The file is saved in a shared volume by Fast API for later retrieval by the user. 

The summarized transcript is stored in Redis using the UUID as the corresponding key. 
Users can query Fast API about the job status and access the final result once it's available.

## Getting Started 
These instructions will help you get this project running on a local machine.
(Work in progress)

### Prerequisites
- [Python 3.10](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

### Installing
1. Clone the repository to your local machine:
    ```bash
    git clone https://github.com/<your-username>/audio_text_summarizer
    ```
2. Navigate to the project directory:
    ```bash
    cd audio_text_summarizer
    ```
3. Kubernetes:
    ```bash
    kubectl start
    kubectl create configmap app-configs --from-env-file=.env 
    kubectl apply -k ./
    ```
   (Note this uses prebuilt images from dockerhub and does not build directly from the source in the repo)

4. Docker-compose
    TODO finish this step

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryproject.org/en/stable/)
- [Whisper](https://graphite.readthedocs.io/en/latest/whisper.html)
- [spaCy](https://spacy.io/)
- [Redis](https://redis.io/)

## Contributing

If you'd like to contribute to this project, please feel free to fork the repository and create 
a pull request with your changes. 
This is a work in progress--any feedback and suggestions are welcomed.


### Notes and basic troubleshooting
This project can be run using either docker-compose or kubernetes.

#### Random Notes

Visit the FastAPI Swagger UI

minikube service fast-api-service --url


Check Flower Status (this or the other method):

kubectl port-forward deployment/flower 8888:8888

http://localhost:8888/ --> Should show the dashboard for Flower.


Alternatively you can use minikube to handle it:

minikube service fast-api-service --url


Check the logs:
(Useful if you wish to see what is happening on any of the services)

kubectl logs deployment/celery-worker -c celery-worker

Caveats:
No password for Redis or other internal/external authentication.
