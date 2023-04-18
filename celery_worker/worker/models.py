# import json
# from typing import Optional
#
# from pydantic import BaseModel, constr
# TODO finish and use as a validator for both ends of celery
#
# class AudioTranscribeSummary(BaseModel):
#     job_uuid: str
#     summary: str = ''
#     transcription: str = ''
#     original_filename: str
#     ratio: float = 0
#     client_ip: str = ''
#     # 0 is in-progress/not complete and 1 is complete
#     # Constrain value to '0' or '1'
#     status: constr(regex='[01]')
