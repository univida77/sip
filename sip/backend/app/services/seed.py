from sqlmodel import Session, select
from ..core.security import hash_password
from ..core.config   import settings
from ..models.usuario import Usuario
from ..models.finanza import CategoriaFinanciera


def seed_admin(session: Session) -> None:
    if session.exec(select(Usuario).where(Usuario.email == settings.ADMIN_EMAIL)).first():
        return
    session.add(Usuario(
        nombre=settings.ADMIN_NOMBRE, apellidos=settings.ADMIN_APELLIDOS,
        email=settings.ADMIN_EMAIL,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        rol="admin", activo=True,
    ))
    session.commit()
    print(f"✅  Admin: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")


def seed_categorias(session: Session) -> None:
    if session.exec(select(CategoriaFinanciera)).first():
        return
    cats = [
        ("Limosnas", "ingreso"), ("Diezmos", "ingreso"), ("Donaciones", "ingreso"),
        ("Eventos", "ingreso"), ("Servicios sacramentales", "ingreso"), ("Otros ingresos", "ingreso"),
        ("Mantenimiento", "egreso"), ("Servicios básicos", "egreso"), ("Materiales", "egreso"),
        ("Nómina", "egreso"), ("Eventos parroquiales", "egreso"), ("Otros egresos", "egreso"),
    ]
    for nombre, tipo in cats:
        session.add(CategoriaFinanciera(nombre=nombre, tipo=tipo))
    session.commit()
    print(f"✅  {len(cats)} categorías creadas")


def run_seed(session: Session) -> None:
    seed_admin(session)
    seed_categorias(session)
