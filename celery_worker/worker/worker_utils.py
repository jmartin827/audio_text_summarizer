import logging
import os
import time
from heapq import nlargest
from pathlib import Path
from typing import List

import redis
import spacy
# Depreciated whisper for faster whisper variant
# import whisper
from faster_whisper import WhisperModel
from spacy.lang.en.stop_words import STOP_WORDS


def logging_setup():
    # Logging Setup
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Set logging level
    logging.getLogger().setLevel(logging.INFO)


# Start logger
logging_setup()


def get_summary(text_in: str, ratio: float = 0.3, max_tokens: int = 10,
                min_tokens: int = 5) -> List[str]:
    """Loads a string, the desired summarization ratio, and the max tokens.
    A token is a word, punctuation, or whitespace.
    Ratio defines the initial to desired amount of output.
    Model is set to the en_core_web_sm which is faster than the multilingual option
    """
    from string import punctuation
    stopwords = list(STOP_WORDS)
    punctuation = punctuation + '\n'

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text_in)

    tokens = [token.text for token in doc]
    logging.debug(f'Tokens: {tokens}')

    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    logging.debug(f'Word Frequencies: {word_frequencies}')

    sentence_tokens = [sent for sent in doc.sents]
    logging.debug(f'Sentence Tokens: {sentence_tokens}')

    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    # Set select length based off of ratio, min, and max tokens
    select_length = int(len(sentence_tokens) * ratio)

    if select_length <= 0:
        # TODO add in custom exceptions and handling.
        logging.error('Error: Unable to process due too of short recording or too much summarization')
        return ['Audio recording or desired summarization ratio is insufficient. Unable to process file.']

    if min_tokens <= select_length >= max_tokens:
        select_length = max_tokens
        logging.info(f'Token select length greater than {max_tokens}--setting it maximum of {max_tokens}')
    else:
        logging.info(f'select_length already within range:{select_length}')

    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)

    # Merge together
    final_summary = [word.text for word in summary]
    logging.info(f'Final summary: {final_summary}')

    return final_summary


def transcribe_audio(audio_file: Path) -> str:
    """Loads the audio file and returns a transcript as a string
    """
    # TODO get audio sample length for logging info

    logging.info(f'Processing audio file: {audio_file}')

    start = time.time()

    # Whisper AI option:
    # Load model and transcribe audio
    # model = whisper.load_model("tiny.en")
    # result = model.transcribe(f'{audio_file}')
    # text = result["text"]

    # TODO build docker image with model
    model = WhisperModel(model_size_or_path="tiny", compute_type='float32')
    segments, info = model.transcribe(str(audio_file), word_timestamps=True)
    text = ''.join([segment.text for segment in list(segments)])

    elapsed = time.time()
    elapsed_time = round((elapsed - start), 2)

    logging.info(f'Transcription time: {elapsed_time} seconds. Raw Transcription: {text}')
    return text


def get_redis_client(db_num: int) -> redis.Redis:
    """Initialize Redis client.
    DB 0 is Celery
    DB 1 is task status
    DB 2 is for IP rate limiting
    """
    client = redis.Redis(host=os.environ.get('REDIS_HOST'),
                         port=int(os.environ.get('REDIS_PORT')),
                         db=db_num)

    # Select index 1 for Redis DB
    client.execute_command('SELECT', db_num)

    return client

# transcribe_audio('../common_voice_en_34956476.mp3')
