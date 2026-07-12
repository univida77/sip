from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ....core.database  import get_session
from ....core.security  import (hash_password, verify_password,
                                create_access_token, create_refresh_token,
                                decode_token, get_current_user, require_admin)
from ....models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(Usuario).where(Usuario.email == form.username)).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Credenciales incorrectas")
    if not user.activo:
        raise HTTPException(403, "Usuario inactivo")
    user.ultimo_acceso = datetime.now(timezone.utc)
    session.add(user); session.commit()
    return {
        "access_token":  create_access_token(user.id, {"rol": user.rol}),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "rol":    user.rol,
        "nombre": f"{user.nombre} {user.apellidos}".strip(),
    }


@router.post("/refresh")
def refresh(body: dict, session: Session = Depends(get_session)):
    payload = decode_token(body.get("refresh_token", ""))
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Tipo de token incorrecto")
    user = session.get(Usuario, int(payload["sub"]))
    if not user or not user.activo:
        raise HTTPException(401, "Usuario no encontrado")
    return {
        "access_token":  create_access_token(user.id, {"rol": user.rol}),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "rol":    user.rol,
        "nombre": f"{user.nombre} {user.apellidos}".strip(),
    }


@router.get("/me")
def me(current: Usuario = Depends(get_current_user)):
    return {"id": current.id, "nombre": current.nombre, "apellidos": current.apellidos,
            "email": current.email, "rol": current.rol, "activo": current.activo}


@router.post("/cambiar-password")
def cambiar_password(body: dict, current: Usuario = Depends(get_current_user),
                     session: Session = Depends(get_session)):
    if not verify_password(body.get("password_actual", ""), current.password_hash):
        raise HTTPException(400, "Contraseña actual incorrecta")
    current.password_hash = hash_password(body.get("password_nuevo", ""))
    session.add(current); session.commit()
    return {"detail": "Contraseña actualizada"}


@router.post("/register")
def register(body: dict, session: Session = Depends(get_session),
             _: Usuario = Depends(require_admin)):
    if session.exec(select(Usuario).where(Usuario.email == body["email"])).first():
        raise HTTPException(400, "Email ya registrado")
    user = Usuario(nombre=body["nombre"], apellidos=body.get("apellidos", ""),
                   email=body["email"], password_hash=hash_password(body["password"]),
                   rol=body.get("rol", "secretaria"))
    session.add(user); session.commit(); session.refresh(user)
    return {"id": user.id, "nombre": user.nombre, "email": user.email, "rol": user.rol}


@router.get("/usuarios")
def list_usuarios(session: Session = Depends(get_session), _: Usuario = Depends(require_admin)):
    return [{"id": u.id, "nombre": u.nombre, "apellidos": u.apellidos,
             "email": u.email, "rol": u.rol, "activo": u.activo}
            for u in session.exec(select(Usuario).order_by(Usuario.nombre)).all()]
