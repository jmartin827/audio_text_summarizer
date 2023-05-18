import logging
import os
import time
from heapq import nlargest
from pathlib import Path
from typing import List, Optional

import redis
import requests
import spacy
from requests.exceptions import InvalidSchema
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


def query_inference_endpoint(filename: Path, api_token: Optional[str] = None,
                             api_url: Optional[str] = None) -> None | str:
    """Read the file and provide delay if model needs to be loaded.
    Ensures that after a certain amount of time and attempts that it returns None.
    """

    # Set if not given
    if (api_url or api_token) is None:
        api_url, api_token = os.environ.get('API_URL'), os.environ.get('API_TOKEN')

    headers = {"Authorization": f"Bearer {api_token}"}
    # TODO determine if logging this is a security risk
    logging.info(f'Sending transcription to inference endpoint: {api_url} Header: {headers}')

    with open(filename, "rb") as f:
        data = f.read()

    start, attempts = time.time(), 0
    # Returns None if longer than 45 seconds or however the standard warmup period is.
    while True:
        attempts += 1
        current_time = (start - time.time())
        if abs(current_time) >= 60 and attempts >= 3:
            return None

        try:
            response = requests.post(url=api_url, headers=headers, data=data)
            logging.info(f'{response}, {response.text}')
        except (InvalidSchema, requests.exceptions.MissingSchema):
            logging.error(f'There is an issue with either the K8 secrets or .env variables for API_URL. '
                          f'Do not wrap either in single or double quotation marks')
            return None

        response_json = response.json()
        if response.status_code == 503:
            if 'estimated_time' in response_json.keys():
                logging.warning(f'Model needs to be loaded: {response.json()}')
                time.sleep(int(response_json['estimated_time']) + 2)
                continue
            else:
                logging.warning(f'503 without estimated wait time: {response.text}')
                time.sleep(2)
        if response.status_code == 429:
            logging.warning(f'Too many requests. Waiting 2 seconds: {response.text}')
            time.sleep(2)

        # If good response return result
        if response.status_code == 200 and 'text' in response_json.keys():
            logging.info(f'Received transcribed audio response: {response.json()["text"]}')
            return response.json()['text']


if __name__ == '__main__':
    query_inference_endpoint(api_token='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',
                             api_url='https://api-inference.huggingface.co/models/openai/whisper-tiny',
                             filename=Path('../common_voice_en_34956476.mp3'))
