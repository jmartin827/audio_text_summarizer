import logging
import os
from pathlib import Path

from worker import get_celery_setup
from utils import transcribe_audio, get_summary

logging.basicConfig(level='INFO')

process = get_celery_setup()


@process.task
def process_file(audio_task_in: tuple) -> list[str]:
    # TODO refactor so that it hits db with uuid or add further info within variable.

    file_path = Path(f'input/{audio_task_in[0]}')
    transcription = transcribe_audio(audio_file=file_path)
    summary = get_summary(text_in=transcription)
    percent = round((len(" ".join(summary)) / len(transcription)), 2) * 100

    logging.info(f'Resulted in {percent}% of original transcript')

    os.remove(file_path)
    logging.info(f'Cleaned up file {file_path}')

    return summary
