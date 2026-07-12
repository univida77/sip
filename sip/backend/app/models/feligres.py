from typing import Optional
from datetime import datetime, date, timezone
from sqlmodel import SQLModel, Field


class Feligres(SQLModel, table=True):
    __tablename__ = "feligreses"
    id:               Optional[int]  = Field(default=None, primary_key=True)
    nombre:           str            = Field(max_length=100, index=True)
    apellidos:        str            = Field(max_length=150, default="", index=True)
    email:            Optional[str]  = Field(default=None, max_length=200)
    telefono:         Optional[str]  = Field(default=None, max_length=20)
    fecha_nacimiento: Optional[date] = Field(default=None)
    direccion:        Optional[str]  = Field(default=None, max_length=255)
    colonia:          Optional[str]  = Field(default=None, max_length=100)
    ciudad:           Optional[str]  = Field(default=None, max_length=100)
    notas:            Optional[str]  = Field(default=None)
    activo:           bool           = Field(default=True)
    creado_en:        datetime       = Field(default_factory=lambda: datetime.now(timezone.utc))
    actualizado_en:   datetime       = Field(default_factory=lambda: datetime.now(timezone.utc))
