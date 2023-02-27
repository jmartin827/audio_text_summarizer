import celery
from celery import Celery

from utils import logging_setup

logging_setup()


def get_celery_setup() -> celery.Celery:
    """Sets up celery instance and relies on container env vars for configuration.
    """
    return Celery()


if __name__ == "__main__":
    worker = get_celery_setup().Worker()
    worker.start()
