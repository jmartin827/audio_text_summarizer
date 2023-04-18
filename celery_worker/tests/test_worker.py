import logging
from pathlib import Path

from worker.worker_utils import transcribe_audio, logging_setup

logging_setup()


def test_transcribe_simple():
    """Test functionality of transcribe function"""
    logging.info(f'Testing the transcription function...')
    result = transcribe_audio(Path('../common_voice_en_34956476.mp3'))
    assert result.strip() == 'Only time will tell.'


def test_transcribe_simple_fail():
    """Test functionality of transcribe function"""
    logging.info(f'Testing the transcription function...')
    result = transcribe_audio(Path('../common_voice_en_34956476.mp3'))
    assert result.strip() != 'Only word will tell.'
