import json
import logging
import os
from pathlib import Path

import pydantic

from worker import get_celery_setup
from models import AudioTaskValidator
from worker_utils import transcribe_audio, get_summary, logging_setup, get_redis_client

logging_setup()

process = get_celery_setup()


@process.task
def process_file(audio_task_in: dict) -> str | None:  # TODO find better type hint for json
    """Passes file UUID to transcription function and result to summarization function.

    """
    # TODO output more data such as phrase-level timestamps
    file_state = audio_task_in
    logging.info(f'Received job info:{audio_task_in}')

    # Update Redis entry to in-progress
    client = get_redis_client(db_num=int(os.environ.get('REDIS_DB')))

    # Set entry and expire time of 5 minutes
    client.setex(name=file_state['job_uuid'], time=300, value='Processing')
    file_path = Path(f'../input/{file_state["job_uuid"]}')

    # Transcribe audio and validate. If error cleanup and set job to 'Error' status
    try:
        AudioTaskValidator(**audio_task_in)
        transcription = transcribe_audio(audio_file=file_path)
    except (RuntimeError, pydantic.error_wrappers.ValidationError) as e:
        logging.error(f'File is either empty or unable to process {e}')
        client.setex(name=file_state['job_uuid'], time=15, value='Error')
        os.remove(file_path)
        logging.info(f'Cleaned up file {file_path}')
        return None

    # Convert to string for Redis
    summary = ' '.join(get_summary(text_in=transcription, ratio=file_state["ratio"]))

    # file_state
    file_state = {**file_state, 'summary': summary,
                  'transcription': transcription,
                  'status': 1}

    os.remove(file_path)
    logging.info(f'Cleaned up file {file_path}')

    # Put final result into Redis using UUID as the key and expire to 10 minutes
    client.setex(name=file_state['job_uuid'], time=600, value=json.dumps(file_state))

    # Remove job from client IP quota/throttle
    client = get_redis_client(db_num=int(os.environ.get('REDIS_DB_IP')))
    logging.info(f'Removing Job from client IP quota: {file_state["client_ip"]}')
    client.lrem(str(file_state['client_ip']), 0, str(file_state['job_uuid']))

    # Log Info
    que_info = [item.decode() for item in client.lrange(file_state["client_ip"], 0, -1)]
    que_count = client.llen(file_state["client_ip"])
    logging.info(f'Que Left for {file_state["client_ip"]}: {que_info} Count: {que_count}')

    return summary
