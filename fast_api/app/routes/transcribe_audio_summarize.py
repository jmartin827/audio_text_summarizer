import logging
import os
import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile

import aiofiles
from fastapi import APIRouter, HTTPException, Form
from fastapi import File, UploadFile

from app.celery_worker.tasks import process_file
from app.utils import transcribe_audio, get_summary

from app.models import AudioTask

router = APIRouter()
logging.basicConfig(level='INFO')


@router.post('/process')
# Async with chunking as per:
# TODO verify and improve
# https://stackoverflow.com/questions/63580229/how-to-save-uploadfile-in-fastapi
async def process(in_file: UploadFile = File(...), summary_ratio: float = Form(...)):
    if in_file.content_type not in ['audio/flac', 'audio/wav', 'audio/mp3']:
        raise HTTPException(400, detail="Invalid document type")

    # Ensures summary ratio is reasonable
    if not 0.01 <= summary_ratio <= 1:
        raise HTTPException(400, detail="Summary Ratio must be between 1 and 0.01!")

    file_name, file_extension = os.path.splitext(in_file.filename)
    audio_task = AudioTask(
        task_uuid=uuid.uuid1(),
        task_file_name=file_name,
        task_file_extension=file_extension,
        task_ratio=summary_ratio
    )

    async with aiofiles.open(f'{audio_task.task_uuid}', 'wb') as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    # Queue file processing task
    result = process_file.delay(audio_task_in=audio_task)
    return {'task_id': result.id}
