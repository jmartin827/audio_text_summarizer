# Transcribe audio
import logging
from pathlib import Path
from typing import Optional

from worker_utils import transcribe_audio, logging_setup


class WorkerProblem(Exception):
    logging.warning('Worker appears unresponsive!')
    pass


def initialize_test_worker(file_input: Optional[str] = '../common_voice_en_34956476.mp3'):
    """Forces Whisper to download the initial model on container creation.
    Useful for testing if service is online as well.
    """
    file_path = Path(file_input)
    transcription = transcribe_audio(audio_file=file_path)
    # Verified that if ran by K8s as a status check that failure will result in non 0 exit status
    if transcription.strip() != 'Only time will tell.':
        raise WorkerProblem
    logging.info('Initialized worker')


if __name__ == '__main__':
    logging_setup()
    initialize_test_worker()
