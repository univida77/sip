from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"
    id:            Optional[int]      = Field(default=None, primary_key=True)
    nombre:        str                = Field(max_length=100)
    apellidos:     str                = Field(max_length=150, default="")
    email:         str                = Field(max_length=200, unique=True, index=True)
    password_hash: str                = Field(max_length=255)
    rol:           str                = Field(default="secretaria", max_length=30)
    activo:        bool               = Field(default=True)
    creado_en:     datetime           = Field(default_factory=lambda: datetime.now(timezone.utc))
    ultimo_acceso: Optional[datetime] = Field(default=None)
