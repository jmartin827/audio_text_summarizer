Uses FastAPI to create Celery tasks.

Checks source user's IP VIA middleware to throttle to specified cocurrent jobs
per user.

Able to check job status based on UUID.

Integrates with Celery by communicating with Redis as the task broker.

Logging level set to debug by default and can be changed in fast_api/app/utils.py

Automatically deletes old entries for throttling, jobs, and results through Redis expire time 'ttl'.


