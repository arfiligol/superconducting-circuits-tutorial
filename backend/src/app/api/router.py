from fastapi import APIRouter
from src.app.api.routers.circuit_definitions import router as circuit_definitions_router
from src.app.api.routers.datasets import router as datasets_router
from src.app.api.routers.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(datasets_router)
api_router.include_router(circuit_definitions_router)
