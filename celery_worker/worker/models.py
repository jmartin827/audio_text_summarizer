from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress, constr, confloat, conint, validator
import uuid


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


class AudioTaskValidator(BaseModel):
    job_uuid: str = Field(..., description='UUIDv1 string representation')

    @validator('job_uuid')
    def validate_uuid(cls, value):
        if not is_valid_uuid(value):
            raise ValueError('Invalid UUID format')
        return value

    summary: str = ''
    transcription: str = ''
    original_filename: str = Field(..., description='Path or filename')
    ratio: confloat(ge=0.1, le=1.0)
    client_ip: IPvAnyAddress
    status: conint(ge=0, le=1)
