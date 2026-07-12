from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.models  # noqa
from app.core.config   import settings
from app.core.database import create_db_and_tables
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    print(f"\n🚀  Sistema Parroquial v5.0 [{settings.ENVIRONMENT}]")
    print(f"📦  DB: {settings.database_url}")
    create_db_and_tables()
    from sqlmodel import Session
    from app.core.database import engine
    from app.services.seed import run_seed
    with Session(engine) as session:
        run_seed(session)
    print("✅  Servidor listo → http://localhost:8000")
    print("📖  Docs        → http://localhost:8000/docs\n")
    yield
    print("🛑  Servidor detenido")


app = FastAPI(
    title="Sistema Parroquial API",
    description="Backend para Sistema de Gestión Parroquial v5.0",
    version="5.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# En desarrollo: permite cualquier origen (Flutter Web cambia puerto cada run)
# En producción: usa la lista de ALLOWED_ORIGINS del .env
if settings.is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,   # False requerido cuando allow_origins=["*"]
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "5.0.0", "env": settings.ENVIRONMENT}


@app.get("/", tags=["Root"])
def root():
    return {"message": "Sistema Parroquial API v5.0 — docs en /docs"}
