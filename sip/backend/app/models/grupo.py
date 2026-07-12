from typing import Optional
from datetime import datetime, date, time, timezone
from sqlmodel import SQLModel, Field


class Grupo(SQLModel, table=True):
    __tablename__ = "grupos"
    id:           Optional[int]  = Field(default=None, primary_key=True)
    nombre:       str            = Field(max_length=150, index=True)
    tipo:         str            = Field(max_length=50, default="ministerio")
    descripcion:  Optional[str]  = Field(default=None)
    lider_id:     Optional[int]  = Field(default=None, foreign_key="feligreses.id")
    dia_reunion:  Optional[str]  = Field(default=None, max_length=20)
    hora_reunion: Optional[time] = Field(default=None)
    lugar:        Optional[str]  = Field(default=None, max_length=200)
    activo:       bool           = Field(default=True)
    creado_en:    datetime       = Field(default_factory=lambda: datetime.now(timezone.utc))


class MiembroGrupo(SQLModel, table=True):
    __tablename__ = "miembros_grupo"
    id:            Optional[int] = Field(default=None, primary_key=True)
    grupo_id:      int           = Field(foreign_key="grupos.id", index=True)
    feligres_id:   int           = Field(foreign_key="feligreses.id", index=True)
    rol_en_grupo:  str           = Field(default="miembro", max_length=50)
    fecha_ingreso: date          = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    activo:        bool          = Field(default=True)


class Sesion(SQLModel, table=True):
    __tablename__ = "sesiones"
    id:        Optional[int] = Field(default=None, primary_key=True)
    grupo_id:  int           = Field(foreign_key="grupos.id", index=True)
    fecha:     date          = Field(index=True)
    tema:      Optional[str] = Field(default=None, max_length=255)
    notas:     Optional[str] = Field(default=None)
    realizada: bool          = Field(default=True)
    creado_en: datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))


class Asistencia(SQLModel, table=True):
    __tablename__ = "asistencias"
    id:          Optional[int] = Field(default=None, primary_key=True)
    sesion_id:   int           = Field(foreign_key="sesiones.id", index=True)
    feligres_id: int           = Field(foreign_key="feligreses.id", index=True)
    presente:    bool          = Field(default=True)
    justificada: bool          = Field(default=False)
    nota:        Optional[str] = Field(default=None, max_length=255)
