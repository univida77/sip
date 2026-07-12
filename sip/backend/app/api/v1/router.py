from fastapi import APIRouter
from .endpoints import auth, feligreses, finanzas, inventario, actas, grupos, reportes, sync

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(feligreses.router)
api_router.include_router(grupos.router)
api_router.include_router(finanzas.router)
api_router.include_router(inventario.router)
api_router.include_router(actas.router)
api_router.include_router(reportes.router)
api_router.include_router(sync.router)
