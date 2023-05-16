Celery Worker Local Processing

This Docker image runs a Celery worker that takes tasks from a queue, processes them locally using Whisper AI, 
updates the task status, and does the summarization using Spacy.

Note that 'openai-whisper' was depreciated out in favor of 'faster-whisper'.
If you wish to switch simply go to the files below, comment out the current code, and uncomment the referenced code:

requirements.txt:
# Whisper AI Option
#  openai-whisper==20230314

celery_worker/worker/worker_utils.py

# import whisper
(...)
# model = whisper.load_model("tiny.en")
# result = model.transcribe(f'{audio_file}')
# text = result["text"]