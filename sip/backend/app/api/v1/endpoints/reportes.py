from typing import Optional
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from ....core.database   import get_session
from ....core.security   import get_current_user
from ....models.feligres import Feligres
from ....models.grupo    import Grupo, Sesion, Asistencia, MiembroGrupo
from ....models.finanza  import MovimientoFinanciero
from ....models.inventario import ItemInventario

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/dashboard")
def dashboard(session: Session = Depends(get_session), _=Depends(get_current_user)):
    now   = datetime.now(timezone.utc)
    inicio = f"{now.year}-{now.month:02d}-01"
    total_f = session.exec(select(func.count(Feligres.id)).where(Feligres.activo == True)).one()
    total_g = session.exec(select(func.count(Grupo.id)).where(Grupo.activo == True)).one()
    ing = session.exec(select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
                       .where(MovimientoFinanciero.tipo == "ingreso",
                              MovimientoFinanciero.fecha >= inicio)).one()
    egr = session.exec(select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
                       .where(MovimientoFinanciero.tipo == "egreso",
                              MovimientoFinanciero.fecha >= inicio)).one()
    items = session.exec(select(func.count(ItemInventario.id))
                         .where(ItemInventario.activo == True)).one()
    return {"total_feligreses": total_f, "total_grupos": total_g,
            "sacramentos_mes": 0, "ingresos_mes": float(ing), "egresos_mes": float(egr),
            "balance_mes": float(ing)-float(egr), "items_inventario": items}


@router.get("/finanzas/tendencia-mensual")
def tendencia(meses: int = Query(6, ge=1, le=24),
              session: Session = Depends(get_session), _=Depends(get_current_user)):
    result = []
    hoy = date.today().replace(day=1)
    for i in range(meses-1, -1, -1):
        ini = hoy - relativedelta(months=i)
        fin = ini + relativedelta(months=1, days=-1)
        ing = session.exec(select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
                           .where(MovimientoFinanciero.tipo == "ingreso",
                                  MovimientoFinanciero.fecha >= str(ini),
                                  MovimientoFinanciero.fecha <= str(fin))).one()
        egr = session.exec(select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
                           .where(MovimientoFinanciero.tipo == "egreso",
                                  MovimientoFinanciero.fecha >= str(ini),
                                  MovimientoFinanciero.fecha <= str(fin))).one()
        result.append({"mes": ini.strftime("%b %Y"), "ingresos": float(ing),
                        "egresos": float(egr), "balance": float(ing)-float(egr)})
    return result


@router.get("/sacramentos/distribucion")
def distribucion_sacramentos(_=Depends(get_current_user)):
    return []


@router.get("/asistencia/promedio-grupos")
def promedio_asistencia(session: Session = Depends(get_session), _=Depends(get_current_user)):
    grupos = session.exec(select(Grupo).where(Grupo.activo == True)).all()
    result = []
    for g in grupos:
        total_s = session.exec(select(func.count(Sesion.id)).where(Sesion.grupo_id == g.id)).one()
        if not total_s: continue
        sesion_ids = [s.id for s in session.exec(
            select(Sesion.id).where(Sesion.grupo_id == g.id)).all()]
        total_m = session.exec(select(func.count(MiembroGrupo.id))
                               .where(MiembroGrupo.grupo_id == g.id,
                                      MiembroGrupo.activo == True)).one()
        presentes = session.exec(select(func.count(Asistencia.id))
                                 .where(Asistencia.sesion_id.in_(sesion_ids),
                                        Asistencia.presente == True)).one()
        total_pos = total_s * max(total_m, 1)
        result.append({"grupo_id": g.id, "grupo": g.nombre, "tipo": g.tipo,
                        "total_sesiones": total_s,
                        "promedio": round(presentes/total_pos*100, 1) if total_pos else 0})
    return sorted(result, key=lambda x: x["promedio"], reverse=True)


@router.get("/catequesis/avance")
def avance_catequesis(_=Depends(get_current_user)):
    return []
