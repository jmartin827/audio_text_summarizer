Transcribes audio and returns summarized text.
Uses Fast API, Celery, Whisper, spaCY, and Redis.
Currently, everything can be run/tested using Docker Compose.

An audio file is uploaded to Fast API along with the desired summarization ratio and
a UUID for the file is returned which can be used to check the job status.
A task is sent to Redis from Fast API which functions as a message broker, a Celery worker
consumes the task from the que, and uses the UUID to identify the correlating file which was
saved in a shared volume by Fast API.

The final result--the summarized transcript is stored in Redis using the UUID as the 
corresponding key. Fast API can be queried about the status of the job and once ready
the final result is available.

This is a work in progress which was done over the weekend and needs time to finish.
