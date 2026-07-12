from math import ceil
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from ....core.database  import get_session
from ....core.security  import get_current_user, require_secretaria
from ....models.usuario import Usuario
from ....models.finanza import MovimientoFinanciero, CategoriaFinanciera

router = APIRouter(prefix="/finanzas", tags=["Finanzas"])


@router.get("/movimientos")
def list_movimientos(page: int = Query(1, ge=1), size: int = Query(20, le=100),
                     tipo: Optional[str] = None, fecha_desde: Optional[str] = None,
                     fecha_hasta: Optional[str] = None,
                     session: Session = Depends(get_session), _=Depends(get_current_user)):
    q = select(MovimientoFinanciero)
    if tipo:        q = q.where(MovimientoFinanciero.tipo == tipo)
    if fecha_desde: q = q.where(MovimientoFinanciero.fecha >= fecha_desde)
    if fecha_hasta: q = q.where(MovimientoFinanciero.fecha <= fecha_hasta)
    total = session.exec(select(func.count()).select_from(q.subquery())).one()
    items = session.exec(q.order_by(MovimientoFinanciero.fecha.desc())
                         .offset((page-1)*size).limit(size)).all()
    result = []
    for m in items:
        cat = session.get(CategoriaFinanciera, m.categoria_id) if m.categoria_id else None
        result.append({"id": m.id, "tipo": m.tipo, "concepto": m.concepto, "monto": m.monto,
                       "fecha": str(m.fecha), "categoria": cat.nombre if cat else None,
                       "notas": m.notas, "creado_en": m.creado_en.isoformat()})
    return {"items": result, "total": total, "page": page, "size": size,
            "pages": ceil(total/size) if total else 1}


@router.post("/movimientos", status_code=201)
def create_movimiento(body: dict, session: Session = Depends(get_session),
                      current: Usuario = Depends(require_secretaria)):
    m = MovimientoFinanciero(tipo=body["tipo"], concepto=body["concepto"],
                             monto=float(body["monto"]), fecha=body["fecha"],
                             categoria_id=body.get("categoria_id"),
                             notas=body.get("notas"), registrado_por=current.id)
    session.add(m); session.commit(); session.refresh(m)
    return {"id": m.id, "tipo": m.tipo, "concepto": m.concepto, "monto": m.monto,
            "fecha": str(m.fecha), "categoria": None, "creado_en": m.creado_en.isoformat()}


@router.get("/resumen/mes-actual")
def resumen_mes(session: Session = Depends(get_session), _=Depends(get_current_user)):
    now    = datetime.now(timezone.utc)
    inicio = f"{now.year}-{now.month:02d}-01"
    ing = session.exec(select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
                       .where(MovimientoFinanciero.tipo == "ingreso",
                              MovimientoFinanciero.fecha >= inicio)).one()
    egr = session.exec(select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
                       .where(MovimientoFinanciero.tipo == "egreso",
                              MovimientoFinanciero.fecha >= inicio)).one()
    tot = session.exec(select(func.count(MovimientoFinanciero.id))
                       .where(MovimientoFinanciero.fecha >= inicio)).one()
    return {"ingresos": float(ing), "egresos": float(egr),
            "balance": float(ing)-float(egr), "total_movimientos": tot}


@router.get("/categorias")
def list_categorias(session: Session = Depends(get_session), _=Depends(get_current_user)):
    return [{"id": c.id, "nombre": c.nombre, "tipo": c.tipo}
            for c in session.exec(select(CategoriaFinanciera)
                                  .where(CategoriaFinanciera.activa == True)).all()]
