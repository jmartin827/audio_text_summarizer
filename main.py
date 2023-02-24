import logging
from pathlib import Path

from utils import transcribe_audio, get_summary

if __name__ == '__main__':
    # may require: python -m spacy download en_core_web_sm
    logging.basicConfig(level='DEBUG')

    file_path = Path('JFK_inaugural_address.flac')
    # Transcribe audio to text
    transcription = transcribe_audio(audio_file=file_path)

    # Summarize text
    get_summary(text_in=transcription, ratio=0.2, max_tokens=10)
