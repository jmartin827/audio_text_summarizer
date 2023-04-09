import json
import logging
import os
from pathlib import Path

from celery import signals

from utils import transcribe_audio, get_summary, logging_setup, get_redis_client
from worker import get_celery_setup

logging_setup()

process = get_celery_setup()


@process.task
def process_file(audio_task_in: str) -> str:  # TODO find better type hint for json
    """Passes file UUID to transcription function and result to summarization function.

    """
    # TODO create verification model against the json string once loaded back

    file_state = json.loads(audio_task_in)
    logging.info(f'Received job info:{file_state}')

    # Update Redis entry to in-progress
    client = get_redis_client()
    client.set(file_state['job_uuid'], 'In Progress...')
    file_path = Path(f'../input/{file_state["job_uuid"]}')

    # Transcribe audio
    transcription = transcribe_audio(audio_file=file_path)

    # Convert to string for Redis
    summary = ' '.join(get_summary(text_in=transcription, ratio=file_state["ratio"]))
    percent = round((len(" ".join(summary)) / len(transcription)), 2) * 100

    # file_state
    file_state = {**file_state, 'summary': summary,
                  'transcription': transcription,
                  'status': 1}

    logging.info(f'Resulted in {percent}% of original transcript')

    os.remove(file_path)
    logging.info(f'Cleaned up file {file_path}')

    # Put final result into Redis using UUID as the key
    client.set(file_state['job_uuid'], json.dumps(file_state))

    return summary
