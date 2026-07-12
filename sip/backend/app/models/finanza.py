from typing import Optional
from datetime import datetime, date, timezone
from sqlmodel import SQLModel, Field


class CategoriaFinanciera(SQLModel, table=True):
    __tablename__ = "categorias_financieras"
    id:     Optional[int] = Field(default=None, primary_key=True)
    nombre: str           = Field(max_length=100, unique=True)
    tipo:   str           = Field(max_length=20)
    activa: bool          = Field(default=True)


class MovimientoFinanciero(SQLModel, table=True):
    __tablename__ = "movimientos_financieros"
    id:             Optional[int] = Field(default=None, primary_key=True)
    tipo:           str           = Field(max_length=20, index=True)
    concepto:       str           = Field(max_length=255)
    monto:          float         = Field()
    fecha:          date          = Field(index=True)
    categoria_id:   Optional[int] = Field(default=None, foreign_key="categorias_financieras.id")
    referencia:     Optional[str] = Field(default=None, max_length=100)
    notas:          Optional[str] = Field(default=None)
    registrado_por: int           = Field(foreign_key="usuarios.id")
    creado_en:      datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))
