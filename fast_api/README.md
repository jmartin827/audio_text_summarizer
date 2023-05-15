# TODO fully document functionality of this service.

Uses FastAPI.

Checks source IP VIA middleware to throttle users to a specified amount of
unprocessed jobs

Able to check job status based on UUID.

Integrates with Celery by communicating with Redis as the task broker.

Logging level set to debug by default and can be changed in fast_api/app/utils.py


