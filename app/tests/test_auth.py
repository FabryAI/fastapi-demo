# Siccome relativamente al testing non ho mai avuto esperienza sul campo, ho colto l'occasione per commentare
# l'intero file per scopo didattico, quindi di apprendimento personale.


from fastapi.testclient import TestClient  # Client di test fornito da FastAPI per simulare richieste HTTP
from app.main import app  # L'app FastAPI da testare
from app.db.database import get_db  # Funzione per ottenere la sessione DB
from app.models.user import User  # Modello utente dal database
from utils import hash_password  # Funzione per hashare la password

client = TestClient(app)  # Crea un client che simula chiamate HTTP all'app

def create_test_user(db, email="auth@test.com", password="supersecret"):
    """Helper: crea un utente test direttamente nel DB"""
    user = db.query(User).filter(User.email == email).first()  # Controlla se l'utente esiste già
    if not user:  # Se non esiste...
        user = User(email=email, hashed_password=hash_password(password))  # Crea nuovo utente
        db.add(user)  # Aggiunge l'utente alla sessione
        db.commit()  # Salva i cambiamenti nel DB
        db.refresh(user)  # Ricarica i dati aggiornati dal DB (es. ID generato)
    return user  # Ritorna l'utente (esistente o appena creato)

def test_login_success():
    # Prepariamo un utente valido nel DB
    db = next(get_db())  # Otteniamo una sessione DB usando il generatore di dipendenza
    test_user = create_test_user(db)  # Creiamo un utente valido per il test

    # facciamo login
    response = client.post(  # Simuliamo una richiesta POST al path /auth/login
        "/auth/login",
        data={"username": test_user.email, "password": "supersecret"},  # Inviamo le credenziali
        headers={"Content-Type": "application/x-www-form-urlencoded"},  # Tipo di form richiesto da OAuth2
    )

    assert response.status_code == 200  # ✅ Il login deve andare a buon fine → status 200
    data = response.json()  # Converto il body della risposta da JSON a dict
    assert "access_token" in data  # ✅ Verifico che il token sia presente nella risposta
    assert data["token_type"] == "bearer"  # ✅ Il tipo di token dovrebbe essere 'bearer'


def test_login_invalid_credentials():
    # tentiamo login con password sbagliata
    response = client.post(  # Richiesta POST simulata verso /auth/login
        "/auth/login",
        data={"username": "auth@test.com", "password": "wrongpassword"},  # Credenziali non valide
        headers={"Content-Type": "application/x-www-form-urlencoded"},  # Form standard per login
    )

    assert response.status_code == 401  # ❌ Deve fallire → codice 401 (Unauthorized)
    assert response.json()["detail"] == "Invalid credentials"  # ❌ Messaggio di errore previsto
