# Transcribe audio
import logging
import sys
from pathlib import Path
from typing import Optional

from ffmpeg import Error

from utils import transcribe_audio, logging_setup


def initial_download_model(file_input: Optional[str] = 'initialize.flac'):
    """Forces Whisper to download the initial model on container creation"""
    file_path = Path(file_input)
    try:
        transcription = transcribe_audio(audio_file=file_path)
        logging.info('Initialized worker')
    # Will error out as file is empty. TODO use spoken audio file to test if worker is alive.
    except RuntimeError as e:
        pass


if __name__ == '__main__':
    logging_setup()
    initial_download_model()
