import os
import pytest

# Forza i test a usare il Postgres locale "testdb"
os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/testdb"

from app.core.config import settings


@pytest.fixture(scope="session")
def db_url():
    """
    Ritorna la stringa di connessione del DB usata nei test.
    Utile se vuoi passare la connessione a SQLAlchemy o ad altri componenti.
    """
    return settings.DATABASE_URL
