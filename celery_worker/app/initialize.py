# Transcribe audio
import logging
import sys
from pathlib import Path
from typing import Optional

from utils import transcribe_audio, logging_setup


def initial_download_model(file_input: Optional[str] = 'initialize.flac'):
    """Forces Whisper to download the initial model on container creation"""
    file_path = Path(file_input)
    try:
        transcription = transcribe_audio(audio_file=file_path)
    except:
        # Will always result in an error as empty file is used to initiate
        # TODO find open source test file which says "OK" for small validation
        pass

    logging.info(f'Initialized container using empty .flac file.')
    sys.exit(0)


if __name__ == '__main__':
    logging_setup()
    initial_download_model()
