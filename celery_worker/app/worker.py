import celery
from celery import Celery

"""Must be ran from ./fast_api and this command:
celery -A app.celery_worker.tasks.worker worker --loglevel=info

Tensorflow needs threads when using Celery
celery worker -A your_application --pool threads --loginfo=INFO
https://stackoverflow.com/questions/45459205/keras-predict-not-returning-inside-celery-task
"""


def get_celery_setup() -> celery.Celery:
    """Sets up celery as it is sensitive to import configuration
    Currently pickling and NOT using JSON serialization at this time as it won't support
    pydantic models.
    TODO verify everything and cleanup
    TODO consider storing the info on Redis DB and just reference to the UUID
    """
    celery_out = Celery(
        task_serializer="pickle",
        result_serializer="pickle",
        event_serializer="pickle",  # TODO change back to json is not needed
        accept_content=["application/json", "application/x-python-serialize"],
        result_accept_content=["application/json", "application/x-python-serialize"],
        broker_url="redis://redis:6379/0",
        backend_url="redis://redis:6379/0",
        celery_imports="tasks.process_file"
    )
    # celery_out.config_from_object(CeleryConfig())

    return celery_out


if __name__ == "__main__":
    worker = get_celery_setup().Worker()
    worker.start()
