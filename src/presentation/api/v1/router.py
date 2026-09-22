from fastapi import APIRouter
from src.presentation.api.v1.controllers.chat_controller import router as chat_router
from src.presentation.api.v1.controllers.property_controller import router as property_router
from src.presentation.api.v1.controllers.auth_controller import router as auth_router
from src.presentation.api.v1.controllers.staff_controller import router as staff_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(chat_router)
api_v1_router.include_router(property_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(staff_router)

# Alias para compatibilidad con el frontend actual (/api/chat, /api/auth, etc.)
api_legacy_router = APIRouter(prefix="/api")
api_legacy_router.include_router(chat_router)
api_legacy_router.include_router(property_router)
api_legacy_router.include_router(auth_router)
