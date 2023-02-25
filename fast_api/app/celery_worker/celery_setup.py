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
        'app_name',
        broker="redis://127.0.0.1:6379/0",
        backend="redis://127.0.0.1:6379/0",
    )

    CELERY_ACCEPT_CONTENT = ['pickle']
    CELERY_IMPORTS = [
        'app_name.tasks',
    ]

    # Go with pickling instead of JSON serialization so Pydantic models supported
    class CeleryConfig:
        task_serializer = "pickle"
        result_serializer = "pickle"
        event_serializer = "json"
        accept_content = ["application/json", "application/x-python-serialize"]
        result_accept_content = ["application/json", "application/x-python-serialize"]

    celery_out.config_from_object(CeleryConfig)

    return celery_out
