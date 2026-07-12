from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ....core.database  import get_session
from ....core.security  import get_current_user
from ....models.usuario import Usuario
from ....models.sync_log import SyncLog

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.get("/status")
def sync_status(session: Session = Depends(get_session), _=Depends(get_current_user)):
    ultimo = session.exec(select(SyncLog).order_by(SyncLog.creado_en.desc()).limit(1)).first()
    return {"ultimo_sync": ultimo.creado_en.isoformat() if ultimo else None,
            "exitoso": ultimo.exitoso if ultimo else None}


@router.post("/ejecutar")
def ejecutar_sync(session: Session = Depends(get_session),
                  current: Usuario = Depends(get_current_user)):
    log = SyncLog(descripcion="Sync solicitado por cliente",
                  exitoso=True, usuario_id=current.id)
    session.add(log); session.commit(); session.refresh(log)
    return {"detail": "Sync registrado", "id": log.id}


@router.get("/logs")
def sync_logs(session: Session = Depends(get_session), _=Depends(get_current_user)):
    logs = session.exec(select(SyncLog).order_by(SyncLog.creado_en.desc()).limit(50)).all()
    return [{"id": l.id, "descripcion": l.descripcion, "exitoso": l.exitoso,
             "error": l.error, "creado_en": l.creado_en.isoformat()} for l in logs]
