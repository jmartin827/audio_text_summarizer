import logging
import os
import uuid
from typing import Dict

import aiofiles
import celery
from fastapi import APIRouter, HTTPException, Form
from fastapi import File, UploadFile

from app.utils import logging_setup, get_redis_client

router = APIRouter()

logging_setup()


def get_celery_setup() -> celery.Celery:
    """Sets up celery as it is sensitive to import configuration.
    """
    celery_out = celery.Celery()

    class CeleryConfig:
        broker_url = os.environ.get('CELERY_BROKER_URL'),
        backend_url = os.environ.get('CELERY_BACKEND_URL'),
        celery_imports = os.environ.get('CELERY_IMPORTS'),

    celery_out.config_from_object(CeleryConfig())
    return celery_out


@router.post('/process')
async def process(in_file: UploadFile = File(...), summary_ratio: float = Form(...)) -> Dict:
    """Accepts a file upload, verifies inputs, and adds task to Celery que
    """

    if in_file.content_type not in ['audio/flac', 'audio/wav', 'audio/mp3']:
        raise HTTPException(400, detail="Invalid document type")

    # Ensures summary ratio is reasonable
    if not 0.01 <= summary_ratio <= 1:
        raise HTTPException(400, detail="Summary Ratio must be between 1 and 0.01!")

    task_uuid = uuid.uuid1()
    # TODO validate this against a model.
    #   Note models cannot be easily used with Celery--validate here for now.
    file_info_out = (task_uuid, in_file.filename, summary_ratio)

    async with aiofiles.open(f'app/input/{task_uuid}', 'wb') as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk
        logging.info(f'Wrote file {task_uuid} with original filename {file_info_out[1]}')

    # Queue file processing task
    app = get_celery_setup()

    process_file = app.signature('tasks.process_file')

    # This Celery task will continue in the background
    process_file.delay(audio_task_in=file_info_out)

    return {'Processing': task_uuid}


@router.get('/result')
async def get_result(task_uuid: str):
    # TODO ensure the input cannot be used maliciously against redis
    client = get_redis_client()
    result = client.get(task_uuid)

    if result:
        logging.info(f'Redis Value for the UUID:{result}')
        return result

    raise HTTPException(400, detail="UUID invalid or task not yet queued")
