from fastapi import FastAPI
from app.routers import users, auth, projects, tasks, reports
from app.db.base import Base
from app.db.database import engine
from app.db.init_db import init_db
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# Popolo il db così avete modo di testare direttamente
init_db()

app = FastAPI(title="Project Task Management API", version= "1.0.0")

# Registra un gestore personalizzato per gli errori di validazione delle richieste
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []

    # Cicla attraverso ciascun errore di validazione
    for e in exc.errors():
        err = e.copy()  # Fa una copia del dizionario dell'errore

        # Se l'errore contiene un contesto ("ctx") con una chiave "error"
        if "ctx" in err and "error" in err["ctx"]:
            # Converte l'oggetto "error" in stringa per evitare problemi di serializzazione
            err["ctx"]["error"] = str(err["ctx"]["error"])

        # Aggiunge l'errore normalizzato alla lista
        errors.append(err)

    # Restituisce una risposta JSON con status 400 e una struttura chiara
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,  # Override dello status (default sarebbe 422)
        content={
            "detail": "Invalid input",  # Messaggio generico
            "errors": errors,           # Lista dettagliata degli errori di validazione
            "body": exc.body if hasattr(exc, "body") else None  # Il corpo della richiesta, se disponibile
        },
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(reports.router)
