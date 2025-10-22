# app/api/routers/report.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.task import Task
from app.models.project import Project
from app.schemas.report import ProjectTotal
import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/report", tags=["Reports"])

    
@router.get(
    "",
    response_model=list[ProjectTotal],
    responses={
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"},
    },
)
def get_report(
    db: Session = Depends(get_db),
    datetimeStart: datetime = Query(...),
    datetimeEnd: datetime = Query(...),
    current_user: str = Depends(get_current_user)
):
    if datetimeEnd < datetimeStart:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")

    try:
        query = (
            db.query(
                Project.id.label("project"),
                func.sum(func.extract("epoch", Task.end_time - Task.start_time)).label("total"),
            )
            .join(Project, Project.id == Task.project_id)
            .filter(Task.start_time >= datetimeStart, Task.end_time <= datetimeEnd)
            .group_by(Project.id)
        )
        results = query.all()
        return results
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Unexpected database error while generating report")


@router.get(
    "/gantt",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "No tasks found for this user"},
        500: {"description": "Internal server error"},
    },
)
def get_gantt_report(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Restituisce un grafico Gantt per l'utente attualmente loggato.
    """
    try:
        # Recupero tutti i task dell’utente loggato
        tasks = (
            db.query(Task)
            .join(Project, Project.id == Task.project_id)
            .filter(Task.user_id == current_user.id)
            .all()
        )

        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found for this user")

        # Preparo i dati per il grafico
        data = [
            {
                "Task": f"{t.activity} - {t.project.name}",
                "Start": t.start_time,
                "End": t.end_time,
            }
            for t in tasks
        ]
        df = pd.DataFrame(data)

        # Creazione grafico Gantt
        sns.set_theme(style="whitegrid") # Tema per il grafico
        fig, ax = plt.subplots(figsize=(12, 6)) # fig: oggetto generle della figura ax: è il grafico

        for i, row in df.iterrows(): # i: indice riga, row: riga. Scorre il DataFrame, per ogni riga disegna una barra orizzontale con ax.barh 
            ax.barh(
                y=row["Task"],
                width=(row["End"] - row["Start"]).total_seconds() / 3600,
                left=row["Start"],
                height=0.4,
                color=sns.color_palette("husl", len(df))[i],
            )

        # Etichette del grafico
        ax.set_xlabel("Timeline (hours)") 
        ax.set_ylabel("Tasks")
        ax.set_title(f"Gantt chart for {current_user.email}")

        # Sistema il layout atomaticamente evitando errori grafici
        plt.tight_layout()

        # Salvo il grafico in buffer e lo ritorno come PNG
        buf = io.BytesIO() # creo un buffer in memoria (stream di byte)
        plt.savefig(buf, format="png") # salvo il grafico nel buffer in formato PNG
        buf.seek(0) # riporto il cursore all'inizio del buffer
        plt.close(fig) # chiudo la figura per liberare memoria

        return StreamingResponse(buf, media_type="image/png") # restituisco il buffer in streaming

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Unexpected database error while generating Gantt report",
        )
