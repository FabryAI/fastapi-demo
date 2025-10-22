from pydantic import BaseModel
import uuid

class ProjectTotal(BaseModel):
    project: uuid.UUID
    total: float   # numero di secondi

    class Config:
        from_attributes = True
