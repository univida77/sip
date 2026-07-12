from typing import Optional
from datetime import datetime, date, timezone
from sqlmodel import SQLModel, Field


class Acta(SQLModel, table=True):
    __tablename__ = "actas"
    id:             Optional[int]      = Field(default=None, primary_key=True)
    titulo:         str                = Field(max_length=255)
    tipo:           str                = Field(max_length=50, default="reunion")
    fecha:          date               = Field(index=True)
    contenido:      str                = Field(default="")
    firmada:        bool               = Field(default=False)
    firmada_en:     Optional[datetime] = Field(default=None)
    firmada_por:    Optional[int]      = Field(default=None, foreign_key="usuarios.id")
    redactada_por:  int                = Field(foreign_key="usuarios.id")
    creado_en:      datetime           = Field(default_factory=lambda: datetime.now(timezone.utc))
    actualizado_en: datetime           = Field(default_factory=lambda: datetime.now(timezone.utc))
