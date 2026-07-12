from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from ....core.database  import get_session
from ....core.security  import get_current_user, require_secretaria
from ....models.usuario import Usuario
from ....models.grupo   import Grupo, MiembroGrupo, Sesion, Asistencia

router = APIRouter(prefix="/grupos", tags=["Grupos"])


def _fmt(g: Grupo) -> dict:
    return {"id": g.id, "nombre": g.nombre, "tipo": g.tipo,
            "descripcion": g.descripcion, "lider_id": g.lider_id,
            "dia_reunion": g.dia_reunion, "lugar": g.lugar,
            "activo": g.activo, "creado_en": g.creado_en.isoformat()}


@router.get("/")
def list_grupos(page: int = Query(1, ge=1), size: int = Query(20, le=100),
                tipo: Optional[str] = None, activo: Optional[bool] = None,
                session: Session = Depends(get_session), _=Depends(get_current_user)):
    q = select(Grupo)
    if tipo:   q = q.where(Grupo.tipo == tipo)
    if activo is not None: q = q.where(Grupo.activo == activo)
    total = session.exec(select(func.count()).select_from(q.subquery())).one()
    items = session.exec(q.order_by(Grupo.nombre).offset((page-1)*size).limit(size)).all()
    return {"items": [_fmt(g) for g in items], "total": total, "page": page,
            "size": size, "pages": ceil(total/size) if total else 1}


@router.post("/", status_code=201)
def create_grupo(body: dict, session: Session = Depends(get_session), _=Depends(require_secretaria)):
    g = Grupo(**{k: v for k, v in body.items() if hasattr(Grupo, k)})
    session.add(g); session.commit(); session.refresh(g)
    return _fmt(g)


@router.patch("/{gid}")
def update_grupo(gid: int, body: dict, session: Session = Depends(get_session),
                 _=Depends(require_secretaria)):
    g = session.get(Grupo, gid)
    if not g: raise HTTPException(404, "Grupo no encontrado")
    for k, v in body.items():
        if hasattr(g, k): setattr(g, k, v)
    session.add(g); session.commit(); session.refresh(g)
    return _fmt(g)


@router.get("/{gid}/miembros")
def list_miembros(gid: int, session: Session = Depends(get_session), _=Depends(get_current_user)):
    items = session.exec(
        select(MiembroGrupo).where(MiembroGrupo.grupo_id == gid, MiembroGrupo.activo == True)
    ).all()
    return [{"id": m.id, "grupo_id": m.grupo_id, "feligres_id": m.feligres_id,
             "rol_en_grupo": m.rol_en_grupo, "fecha_ingreso": str(m.fecha_ingreso),
             "activo": m.activo} for m in items]


@router.post("/{gid}/miembros", status_code=201)
def add_miembro(gid: int, body: dict, session: Session = Depends(get_session),
                _=Depends(require_secretaria)):
    m = MiembroGrupo(grupo_id=gid, feligres_id=body["feligres_id"],
                     rol_en_grupo=body.get("rol_en_grupo", "miembro"))
    session.add(m); session.commit(); session.refresh(m)
    return {"id": m.id, "grupo_id": m.grupo_id, "feligres_id": m.feligres_id}


@router.delete("/{gid}/miembros/{mid}", status_code=204)
def remove_miembro(gid: int, mid: int, session: Session = Depends(get_session),
                   _=Depends(require_secretaria)):
    m = session.get(MiembroGrupo, mid)
    if not m: raise HTTPException(404, "Miembro no encontrado")
    m.activo = False; session.add(m); session.commit()


@router.get("/{gid}/sesiones")
def list_sesiones(gid: int, session: Session = Depends(get_session), _=Depends(get_current_user)):
    items = session.exec(
        select(Sesion).where(Sesion.grupo_id == gid).order_by(Sesion.fecha.desc())
    ).all()
    return [{"id": s.id, "grupo_id": s.grupo_id, "fecha": str(s.fecha),
             "tema": s.tema, "realizada": s.realizada,
             "creado_en": s.creado_en.isoformat()} for s in items]


@router.post("/{gid}/sesiones", status_code=201)
def create_sesion(gid: int, body: dict, session: Session = Depends(get_session),
                  _=Depends(require_secretaria)):
    s = Sesion(grupo_id=gid, fecha=body["fecha"],
               tema=body.get("tema"), notas=body.get("notas"))
    session.add(s); session.commit(); session.refresh(s)
    return {"id": s.id, "grupo_id": s.grupo_id, "fecha": str(s.fecha), "tema": s.tema}


@router.get("/asistencia/sesion/{sesion_id}")
def get_asistencia(sesion_id: int, session: Session = Depends(get_session),
                   _=Depends(get_current_user)):
    items = session.exec(select(Asistencia).where(Asistencia.sesion_id == sesion_id)).all()
    return [{"id": a.id, "sesion_id": a.sesion_id, "feligres_id": a.feligres_id,
             "presente": a.presente, "justificada": a.justificada} for a in items]


@router.post("/asistencia/bulk")
def registrar_asistencia(body: dict, session: Session = Depends(get_session),
                         _=Depends(require_secretaria)):
    sesion_id = body.get("sesion_id")
    for e in session.exec(select(Asistencia).where(Asistencia.sesion_id == sesion_id)).all():
        session.delete(e)
    for r in body.get("registros", []):
        session.add(Asistencia(sesion_id=sesion_id, feligres_id=r["feligres_id"],
                               presente=r.get("presente", True),
                               justificada=r.get("justificada", False), nota=r.get("nota")))
    session.commit()
    return {"detail": f"{len(body.get('registros', []))} registros guardados"}
