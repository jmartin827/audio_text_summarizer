import logging
import uuid

import aiofiles
import celery
from fastapi import APIRouter, HTTPException, Form
from fastapi import File, UploadFile

router = APIRouter()
logging.basicConfig(level='INFO')


def get_celery_setup() -> celery.Celery:
    """Sets up celery as it is sensitive to import configuration.
    TODO verify everything and cleanup
    TODO consider storing the info on Redis DB and just reference to the UUID
    """
    # TODO set the address as a venv instead and see why redis works this way for url

    celery_out = celery.Celery(
        'project',
    )

    # Go with pickling instead of JSON serialization so Pydantic models supported
    class CeleryConfig:
        task_serializer = "json"
        result_serializer = "json"
        event_serializer = "json"
        accept_content = ["application/json", "application/x-python-serialize"]
        result_accept_content = ["application/json", "application/x-python-serialize"]
        broker_url = "redis://redis:6379/0",
        backend_url = "redis://redis:6379/0",
        celery_imports = "tasks.process_file"

    celery_out.config_from_object(CeleryConfig())

    return celery_out


@router.post('/process')
async def process(in_file: UploadFile = File(...), summary_ratio: float = Form(...)) -> str:
    if in_file.content_type not in ['audio/flac', 'audio/wav', 'audio/mp3']:
        raise HTTPException(400, detail="Invalid document type")

    # Ensures summary ratio is reasonable
    if not 0.01 <= summary_ratio <= 1:
        raise HTTPException(400, detail="Summary Ratio must be between 1 and 0.01!")

    task_uuid = uuid.uuid1()
    # TODO validate this against a mode;. Note models cannot be easily used with Celery--validate here for now.
    file_info_out = (task_uuid, in_file.filename, summary_ratio)

    async with aiofiles.open(f'app/input/{task_uuid}', 'wb') as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk
        logging.info(f'Wrote file {task_uuid} with original filename {file_info_out[1]}')

    # Queue file processing task
    app = get_celery_setup()

    process_file = app.signature('tasks.process_file')

    # TODO have this written to a DB and have another endpoint pull the result/status
    result = process_file.delay(audio_task_in=file_info_out)

    return 'File Received. Processing File'
