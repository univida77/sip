from math import ceil
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, or_
from ....core.database   import get_session
from ....core.security   import get_current_user, require_secretaria
from ....models.inventario import ItemInventario

router = APIRouter(prefix="/inventario", tags=["Inventario"])


def _fmt(i: ItemInventario) -> dict:
    return {"id": i.id, "nombre": i.nombre, "descripcion": i.descripcion,
            "categoria": i.categoria, "cantidad": i.cantidad, "unidad": i.unidad,
            "estado": i.estado, "valor": i.valor, "ubicacion": i.ubicacion,
            "activo": i.activo, "creado_en": i.creado_en.isoformat()}


@router.get("/items")
def list_items(page: int = Query(1, ge=1), size: int = Query(20, le=100),
               buscar: Optional[str] = None, estado: Optional[str] = None,
               session: Session = Depends(get_session), _=Depends(get_current_user)):
    q = select(ItemInventario).where(ItemInventario.activo == True)
    if buscar:
        like = f"%{buscar}%"
        q = q.where(or_(ItemInventario.nombre.ilike(like), ItemInventario.categoria.ilike(like)))
    if estado: q = q.where(ItemInventario.estado == estado)
    total = session.exec(select(func.count()).select_from(q.subquery())).one()
    items = session.exec(q.order_by(ItemInventario.nombre).offset((page-1)*size).limit(size)).all()
    return {"items": [_fmt(i) for i in items], "total": total, "page": page,
            "size": size, "pages": ceil(total/size) if total else 1}


@router.post("/items", status_code=201)
def create_item(body: dict, session: Session = Depends(get_session), _=Depends(require_secretaria)):
    item = ItemInventario(**{k: v for k, v in body.items() if hasattr(ItemInventario, k)})
    session.add(item); session.commit(); session.refresh(item)
    return _fmt(item)


@router.patch("/items/{item_id}")
def update_item(item_id: int, body: dict, session: Session = Depends(get_session),
                _=Depends(require_secretaria)):
    item = session.get(ItemInventario, item_id)
    if not item: raise HTTPException(404, "Item no encontrado")
    for k, v in body.items():
        if hasattr(item, k): setattr(item, k, v)
    item.actualizado_en = datetime.now(timezone.utc)
    session.add(item); session.commit(); session.refresh(item)
    return _fmt(item)


@router.get("/estadisticas")
def estadisticas(session: Session = Depends(get_session), _=Depends(get_current_user)):
    total = session.exec(select(func.count(ItemInventario.id))
                         .where(ItemInventario.activo == True)).one()
    buen  = session.exec(select(func.count(ItemInventario.id))
                         .where(ItemInventario.estado == "bueno",
                                ItemInventario.activo == True)).one()
    rep   = session.exec(select(func.count(ItemInventario.id))
                         .where(ItemInventario.estado == "necesita_reparacion",
                                ItemInventario.activo == True)).one()
    valor = session.exec(select(func.coalesce(
        func.sum(ItemInventario.valor * ItemInventario.cantidad), 0))
        .where(ItemInventario.activo == True)).one()
    return {"total_items": total, "buen_estado": buen,
            "necesita_reparacion": rep, "valor_total": float(valor)}
