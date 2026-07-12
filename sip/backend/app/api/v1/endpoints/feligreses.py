from math import ceil
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, or_
from ....core.database  import get_session
from ....core.security  import get_current_user, require_secretaria
from ....models.usuario import Usuario
from ....models.feligres import Feligres

router = APIRouter(prefix="/feligreses", tags=["Feligreses"])


def _fmt(f: Feligres) -> dict:
    return {"id": f.id, "nombre": f.nombre, "apellidos": f.apellidos,
            "email": f.email, "telefono": f.telefono,
            "fecha_nacimiento": str(f.fecha_nacimiento) if f.fecha_nacimiento else None,
            "colonia": f.colonia, "ciudad": f.ciudad, "activo": f.activo,
            "creado_en": f.creado_en.isoformat()}


@router.get("/")
def list_feligreses(page: int = Query(1, ge=1), size: int = Query(20, le=100),
                    buscar: Optional[str] = None, activo: Optional[bool] = None,
                    session: Session = Depends(get_session), _=Depends(get_current_user)):
    q = select(Feligres)
    if buscar:
        like = f"%{buscar}%"
        q = q.where(or_(Feligres.nombre.ilike(like), Feligres.apellidos.ilike(like),
                        Feligres.telefono.ilike(like)))
    if activo is not None:
        q = q.where(Feligres.activo == activo)
    total = session.exec(select(func.count()).select_from(q.subquery())).one()
    items = session.exec(q.order_by(Feligres.apellidos).offset((page-1)*size).limit(size)).all()
    return {"items": [_fmt(f) for f in items], "total": total, "page": page,
            "size": size, "pages": ceil(total/size) if total else 1}


@router.post("/", status_code=201)
def create_feligres(body: dict, session: Session = Depends(get_session),
                    _=Depends(require_secretaria)):
    f = Feligres(**{k: v for k, v in body.items() if hasattr(Feligres, k)})
    session.add(f); session.commit(); session.refresh(f)
    return _fmt(f)


@router.get("/{fid}")
def get_feligres(fid: int, session: Session = Depends(get_session), _=Depends(get_current_user)):
    f = session.get(Feligres, fid)
    if not f: raise HTTPException(404, "Feligrés no encontrado")
    return _fmt(f)


@router.patch("/{fid}")
def update_feligres(fid: int, body: dict, session: Session = Depends(get_session),
                    _=Depends(require_secretaria)):
    f = session.get(Feligres, fid)
    if not f: raise HTTPException(404, "Feligrés no encontrado")
    for k, v in body.items():
        if hasattr(f, k): setattr(f, k, v)
    f.actualizado_en = datetime.now(timezone.utc)
    session.add(f); session.commit(); session.refresh(f)
    return _fmt(f)


@router.delete("/{fid}", status_code=204)
def delete_feligres(fid: int, session: Session = Depends(get_session), _=Depends(require_secretaria)):
    f = session.get(Feligres, fid)
    if not f: raise HTTPException(404, "Feligrés no encontrado")
    f.activo = False; session.add(f); session.commit()
