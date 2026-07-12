from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from .config import settings

_connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=not settings.is_production,
    pool_pre_ping=True,
)

# SQLite: WAL + foreign keys
if "sqlite" in settings.database_url:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(conn, _):
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
