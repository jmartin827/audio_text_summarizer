import json
import logging
import os
import uuid
from typing import Dict

import aiofiles
import celery
from fastapi import APIRouter, HTTPException, Form
from fastapi import Request, File, UploadFile
from starlette import status

from app.utils import logging_setup, get_redis_client, check__limit_job_count

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
async def process(request: Request, in_file: UploadFile = File(...), summary_ratio: float = Form(...)) -> Dict:
    """Accepts a file upload, verifies inputs, and adds task to Celery que.
    Logs the IP address of the client.
    """

    # Track number of jobs per single IP address to throttle use
    client_host_ip = str(request.client.host)

    # Set Job UUID
    task_uuid = str(uuid.uuid1())
    check__limit_job_count(ip_address=client_host_ip, job_uuid=task_uuid)

    if in_file.content_type not in ['audio/flac', 'audio/wav', 'audio/mp3']:
        logging.info(f'Incorrect format {in_file.content_type}')
        raise HTTPException(400, detail="Invalid document type")

    # Ensures summary ratio is reasonable
    if not 0.01 <= summary_ratio <= 1:
        raise HTTPException(400, detail="Summary Ratio must be between 1 and 0.01!")

    # TODO validate this against a model.
    #   Note models cannot be easily used with Celery--validate here and worker side

    data = {
        'job_uuid': task_uuid,
        'summary': '',
        'transcription': '',
        'original_filename': in_file.filename,
        'ratio': summary_ratio,
        'client_ip': client_host_ip,
        'status': 0,  # Not complete/False
    }
    data_str = json.dumps(data)

    async with aiofiles.open(f'../input/{task_uuid}', 'wb') as out_file:
        # Setting larger chunk size
        while content := await in_file.read(8000):
            await out_file.write(content)
        logging.info(f'Wrote file {task_uuid} with original filename {in_file.filename}')

    # Queue file processing task
    app = get_celery_setup()

    # This Celery task will continue in the background
    logging.info(f'Sending Job to Celery Que: {data_str}')
    process_file = app.signature('tasks.process_file')
    process_file.delay(audio_task_in=data_str)

    return {'Processing': task_uuid}


@router.get('/result')
async def get_result(task_uuid: str):
    client = get_redis_client(db_num=int(os.environ.get('REDIS_DB')))
    result = client.get(task_uuid)

    if result:
        logging.info(f'Redis Value for the UUID:{result}')
        return result

    raise HTTPException(400, detail="UUID invalid or task not yet queued")


@router.get('/healthcheck', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'healthcheck': 'OK'}

