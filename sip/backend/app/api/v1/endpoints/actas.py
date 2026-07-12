from math import ceil
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, or_
from ....core.database  import get_session
from ....core.security  import get_current_user, require_secretaria
from ....models.usuario import Usuario
from ....models.acta    import Acta

router = APIRouter(prefix="/actas", tags=["Actas"])


def _fmt(a: Acta) -> dict:
    return {"id": a.id, "titulo": a.titulo, "tipo": a.tipo, "fecha": str(a.fecha),
            "contenido": a.contenido, "firmada": a.firmada,
            "firmada_en": a.firmada_en.isoformat() if a.firmada_en else None,
            "creado_en": a.creado_en.isoformat()}


@router.get("/")
def list_actas(page: int = Query(1, ge=1), size: int = Query(20, le=100),
               buscar: Optional[str] = None, firmada: Optional[bool] = None,
               session: Session = Depends(get_session), _=Depends(get_current_user)):
    q = select(Acta)
    if buscar:   q = q.where(or_(Acta.titulo.ilike(f"%{buscar}%"), Acta.tipo.ilike(f"%{buscar}%")))
    if firmada is not None: q = q.where(Acta.firmada == firmada)
    total = session.exec(select(func.count()).select_from(q.subquery())).one()
    items = session.exec(q.order_by(Acta.fecha.desc()).offset((page-1)*size).limit(size)).all()
    return {"items": [_fmt(a) for a in items], "total": total, "page": page,
            "size": size, "pages": ceil(total/size) if total else 1}


@router.post("/", status_code=201)
def create_acta(body: dict, session: Session = Depends(get_session),
                current: Usuario = Depends(require_secretaria)):
    a = Acta(titulo=body["titulo"], tipo=body.get("tipo", "reunion"),
             fecha=body["fecha"], contenido=body.get("contenido", ""),
             redactada_por=current.id)
    session.add(a); session.commit(); session.refresh(a)
    return _fmt(a)


@router.patch("/{acta_id}")
def update_acta(acta_id: int, body: dict, session: Session = Depends(get_session),
                _=Depends(require_secretaria)):
    a = session.get(Acta, acta_id)
    if not a: raise HTTPException(404, "Acta no encontrada")
    if a.firmada: raise HTTPException(400, "No se puede editar un acta firmada")
    for k, v in body.items():
        if hasattr(a, k): setattr(a, k, v)
    a.actualizado_en = datetime.now(timezone.utc)
    session.add(a); session.commit(); session.refresh(a)
    return _fmt(a)


@router.post("/{acta_id}/firmar")
def firmar_acta(acta_id: int, session: Session = Depends(get_session),
                current: Usuario = Depends(require_secretaria)):
    a = session.get(Acta, acta_id)
    if not a: raise HTTPException(404, "Acta no encontrada")
    if a.firmada: raise HTTPException(400, "El acta ya está firmada")
    a.firmada = True; a.firmada_en = datetime.now(timezone.utc); a.firmada_por = current.id
    session.add(a); session.commit(); session.refresh(a)
    return _fmt(a)
