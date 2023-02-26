import logging
from fastapi import FastAPI
from app.routes.transcribe_audio_summarize import router

app = FastAPI()

# Mount the router at the "/api" path
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    # When running the application directly (not as a container), start the app server
    import uvicorn

    logging.basicConfig(level='INFO')

    uvicorn.run(app, host="0.0.0.0", port=8000)

