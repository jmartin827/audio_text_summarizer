import logging
import os

import celery
from celery import Celery

from worker_utils import logging_setup

logging_setup()


def get_celery_setup() -> celery.Celery:
    """Sets up celery instance and relies on container env vars for configuration.
    """
    return Celery()


if __name__ == "__main__":
    if os.environ.get('REDIS_HOST') is None:
        logging.warning(f'No env variable supplied for host! --> {os.environ.get("REDIS_HOST")}')
    worker = get_celery_setup().Worker()
    worker.start()
