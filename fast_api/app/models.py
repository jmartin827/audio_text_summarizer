import uuid
from typing import Optional

from pydantic import BaseModel


class AudioTask(BaseModel):
    task_uuid: uuid.UUID
    task_file_name: str
    task_file_extension: str
    task_ratio: Optional[float] = 0.3
    # TODO add in processing options later


