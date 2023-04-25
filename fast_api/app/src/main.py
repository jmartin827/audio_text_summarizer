import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from requests import Request

from app.routes.transcribe_audio_summarize import router

app = FastAPI()

# Mount the router at the "/api" path
app.include_router(router, prefix="/api")

origins = [
    "*"
]


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests for debugging
    """
    logging.debug(f"{request.method} {request.url}")
    response = await call_next(request)
    return response


# TODO specify requirements and add domain specific .env variables here
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # When running the application directly (not as a container) start the app server
    import uvicorn

    logging.basicConfig(level='INFO')

    uvicorn.run(app, host="0.0.0.0", port=8000)
