from typing import Optional
from datetime import datetime, date, timezone
from sqlmodel import SQLModel, Field


class ItemInventario(SQLModel, table=True):
    __tablename__ = "inventario"
    id:             Optional[int]  = Field(default=None, primary_key=True)
    nombre:         str            = Field(max_length=200, index=True)
    descripcion:    Optional[str]  = Field(default=None)
    categoria:      Optional[str]  = Field(default=None, max_length=100)
    cantidad:       int            = Field(default=1)
    unidad:         str            = Field(default="pieza", max_length=30)
    estado:         str            = Field(default="bueno", max_length=30)
    valor:          float          = Field(default=0.0)
    ubicacion:      Optional[str]  = Field(default=None, max_length=150)
    fecha_adq:      Optional[date] = Field(default=None)
    notas:          Optional[str]  = Field(default=None)
    activo:         bool           = Field(default=True)
    creado_en:      datetime       = Field(default_factory=lambda: datetime.now(timezone.utc))
    actualizado_en: datetime       = Field(default_factory=lambda: datetime.now(timezone.utc))
