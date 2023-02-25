import logging
import os
from pathlib import Path

from app.celery_worker.celery_setup import get_celery_setup
from app.models import AudioTask
from app.utils import transcribe_audio, get_summary

logging.basicConfig(level='INFO')

worker = get_celery_setup()


@worker.task
def process_file(audio_task_in: AudioTask) -> list[str]:
    logging.info(f'Received task: {audio_task_in.task_uuid} '
                 f'{audio_task_in.task_file_name} {audio_task_in.task_file_extension}')

    file_path = f'app/src/{audio_task_in.task_uuid}'
    transcription = transcribe_audio(audio_file=Path(file_path))
    summary = get_summary(text_in=transcription, ratio=audio_task_in.task_ratio)
    percent = round((len(" ".join(summary)) / len(transcription)), 3) * 100

    logging.info(f'Resulted in {percent}% of original transcript')

    # TODO decide on best type hinting workflow for uuid
    os.remove(file_path)
    logging.info(f'Cleaned up file {file_path}')

    return summary
