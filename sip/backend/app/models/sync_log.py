from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class SyncLog(SQLModel, table=True):
    __tablename__ = "sync_logs"
    id:          Optional[int] = Field(default=None, primary_key=True)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    exitoso:     bool          = Field(default=True)
    error:       Optional[str] = Field(default=None)
    usuario_id:  Optional[int] = Field(default=None, foreign_key="usuarios.id")
    creado_en:   datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))
