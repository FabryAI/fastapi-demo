from pydantic import BaseModel
import uuid

class ProjectCreate(BaseModel):
    name: str

class ProjectOut(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True # permette di mappare gli attributi del modello SQLAlchemy con quelli dello schema Pydantic
