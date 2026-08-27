"""Database configuration and session management."""

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'sow_generator.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def _set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key enforcement for every SQLite connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


event.listen(engine, "connect", _set_sqlite_pragma)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
