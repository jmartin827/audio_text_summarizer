import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, HTTPException, Form
from fastapi import File, UploadFile

from app.utils import transcribe_audio, get_summary

router = APIRouter()
logging.basicConfig(level='INFO')


@router.post("/upload-file/")
# TODO modify so in memory only
# TODO sanitize input for security purposes
# TODO setup so summary granularity is customizable
async def upload_transcribe_summarize_file(file: UploadFile = File(...), summary_ratio: float = Form()):
    """Accepts upload of supported audio files and returns a summarized transcription."""
    logging.info(f'File Format: {file.content_type}')

    if file.content_type not in ['audio/flac', 'audio/wav', 'audio/mp3']:
        raise HTTPException(400, detail="Invalid document type")

    # Ensures summary ratio is reasonable
    if not 0.01 <= summary_ratio <= 1:
        raise HTTPException(400, detail="Summary Ratio must be between 1 and 0.01!")

    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(await file.read())
        temp_file.flush()
        transcription = transcribe_audio(audio_file=Path(temp_file.name))

    summary = get_summary(text_in=transcription, ratio=summary_ratio)

    percent = round((len(" ".join(summary))/len(transcription)), 3) * 100

    # TODO add more options to the API, break out to a Class, set defaults, and remove defaults from here.
    logging.info(f'Resulted in {percent}% of original transcript')

    return {file.filename: summary}
