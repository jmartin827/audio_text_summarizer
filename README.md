# Audio to Text Summarizer

This project allows users to upload an audio file and receive a summarized transcript via FastApi,
along with a UUID that references the job status and provides access to the result.

Fast API sends a task to Redis, which serves as a message broker,
and a Celery worker retrieves the task from the queue using the UUID to identify the corresponding file.
The file is saved in a shared volume with Fast API for later retrieval by Celery worker.

The summarized transcript is stored in Redis by the Celery worker using the UUID as the corresponding key.
Users can query Fast API about the job status and access the final result once it's available.

A ReactJS front end allows the user to upload a file, see the active job status, and the result once finished.

There are some checks (postStart, readinessProbe, etc) within the K8 deployment to help ensure everything is running and that the Celery workers are fully initialized. 


## Getting Started

These instructions will help you get this project running on a local machine.

--> For an actual deployment see kubernetes/ingress/README.md and skip local ingress
deployment. (Use base deployment and deploy ingress resources)
### Prerequisites

- [Python 3.10](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [minikube](https://minikube.sigs.k8s.io/docs/)
- [Node.js](https://nodejs.org/en)
- [npm](https://www.npmjs.com/)
- [docker](https://www.docker.com/)

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
   **Optional for local testing**
   ```bash
   minikube start
   ```
   **Optional for local test proxy:**
   ```bash
   minikube addons enable ingress
   minikube addons enable ingress-dns
   ```
   **Optional for celery_remote processing**

   Requires HuggingFace API key:
   ```bash
    # Load secrets
    kubectl create secret generic my-secret --from-env-file=.env.secrets
   ```

   **Required:**

   Base Deployment:
   Uncomment either Local or Remote Celery Worker in kubernetes/kustomization.yaml
   ```bash
    kubectl apply -k ./kubernetes
    ```
   
   **No proxy**

   Forward FastAPI port for React and local testing:
   ```bash
   kubectl port-forward deployment/fast-api 8000:8000
   ```
   
   **Optional for local test proxy:**

   --> Update local_test_ingress with desired domain name.

   macOS:

   Add entry within /etc/hosts: 
   127.0.0.1 example.com

   Others:

   See if above works and if not use IP address supplied below:
   ```bash
   kubectl get ingress
   ```
   
   Start tunnel:
   ```bash
   minikube tunnel
   ```
4. Build/Push Changes
   If desired a simple script is provided which will push the updated docker images to a specified username
   ```bash
    ./docker-build-push.sh your-dockerhub-username
    ```
5. React
    Install Node dependencies
   ```bash
   cd front_end
   npm install 
   cd ../
   ```
   Optional for proxy:
   
   Set variable within .env.development
   http://127.0.0.1:8000 -> desired domain being proxied


   Start Dev Server    
   ```bash
   npm start --prefix ./front_end
   ```

   Refer to front_end folder's README.md for additional details.
   
## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryproject.org/en/stable/)
- [Whisper](https://github.com/openai/whisper)
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [spaCy](https://spacy.io/)
- [Redis](https://redis.io/)
- [React](https://react.dev/)
- [Material UI (MUI)](https://github.com/mui/material-ui)
- [Minikube](https://minikube.sigs.k8s.io/)
- [Ingress NGINX Controller](https://github.com/kubernetes/ingress-nginx)
- [Kubernetes](https://kubernetes.io/)
- [Mozilla Common Voice](https://github.com/common-voice/common-voice)

## Contributing

If you'd like to contribute to this project, please feel free to fork the repository and create
a pull request with your changes.
This is a work in progress--any feedback and suggestions are welcomed.

### Notes and basic troubleshooting

This project can be run using kubernetes VIA minikube or with some effort starting each container individually.

#### Random Notes

Requires a significant amount of CPU if parsing 10+ minute audio file.
Requires 1 CPU core and 1GB of RAM per Celery Worker.

Visit the FastAPI Swagger UI for documentation and testing:

localhost:8000/docs

Check Flower Status:
```bash
kubectl port-forward deployment/flower 8888:8888
```
Check the logs:
```bash
kubectl logs deployment/celery-worker -c celery-worker
```

