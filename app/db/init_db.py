from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.db import base
from utils import hash_password
from app.models.user import User
from app.models.project import Project

def init_db():
    # Crea le tabelle se non ci sono
    base.Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # Controllo se ci sono già utenti
        if not db.query(User).first():
            demo_user = User(
                email="admin@example.com",
                hashed_password=hash_password("admin123")
            )
            db.add(demo_user)

        # Controllo se ci sono già progetti
        if not db.query(Project).first():
            demo_project = Project(
                name="Progetto di prova"
            )
            db.add(demo_project)

        db.commit()
    finally:
        db.close()
