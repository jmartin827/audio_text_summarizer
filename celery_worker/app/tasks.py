import logging
import os
import uuid
from pathlib import Path

from utils import transcribe_audio, get_summary, logging_setup, get_redis_client
from worker import get_celery_setup

logging_setup()

process = get_celery_setup()


@process.task
def process_file(audio_task_in: tuple[uuid.UUID, str, float]) -> str:
    """Passes file UUID to transcription function and result to summarization function.

    Accepts a tuple using the following format:
    tuple[uuid.UUID, str(original filename), float(summarization ratio))
    """
    # TODO create verification model for both ends as Celery is not readily tolerant of Pydnatic models.

    # Update Redis entry to in-progress
    client = get_redis_client()
    client.set(audio_task_in[0], 'In Progress...')

    file_path = Path(f'input/{audio_task_in[0]}')

    transcription = transcribe_audio(audio_file=file_path)

    # Convert to string for Redis
    summary = ' '.join(get_summary(text_in=transcription, ratio=audio_task_in[2]))
    percent = round((len(" ".join(summary)) / len(transcription)), 2) * 100

    logging.info(f'Resulted in {percent}% of original transcript')

    os.remove(file_path)
    logging.info(f'Cleaned up file {file_path}')

    # Put final result into Redis
    client.set(audio_task_in[0], summary)

    return summary
