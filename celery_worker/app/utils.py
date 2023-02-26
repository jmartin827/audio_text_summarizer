import logging
import time
from heapq import nlargest
from pathlib import Path
from typing import List

import spacy
import whisper
from spacy.lang.en.stop_words import STOP_WORDS

logging.basicConfig(level='INFO')


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
        logging.warning(f'select_length non positive number {select_length}')
        # TODO add in custom exceptions and handling.
        return ['Error: Unable to process due to short recording or too much summarization']

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

    # Load model and transcribe audio
    model = whisper.load_model("tiny.en")
    result = model.transcribe(f'{audio_file}', fp16=False)

    elapsed = time.time()
    elapsed_time = round((elapsed - start), 2)
    logging.info(f'Transcription time: {elapsed_time} seconds. Raw Transcription: {result["text"]}')

    return result["text"]
