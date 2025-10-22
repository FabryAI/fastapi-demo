import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationInfo


class TaskInput(BaseModel):
    project: uuid.UUID
    user: uuid.UUID
    activity: str
    datetimeStart: datetime
    datetimeEnd: datetime

    @field_validator("datetimeEnd")
    @classmethod
    def check_dates(cls, v, info: ValidationInfo): #cls è la classe, v è il valore del campo, e info ti dà i dettagli del contesto di validazione
        start = info.data.get("datetimeStart")
        if start and v <= start:
            raise ValueError("datetimeEnd must be later than datetimeStart")
        return v


class TaskOut(BaseModel):
    id: uuid.UUID
    project: uuid.UUID
    user: uuid.UUID
    activity: str
    datetimeStart: datetime
    datetimeEnd: datetime

    class Config:
        from_attributes = True
