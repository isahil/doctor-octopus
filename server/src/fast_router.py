from fastapi import APIRouter

from src.routers.cards import router as cards_router
from src.routers.notifications import router as notifications_router
from src.routers.system import router as system_router

router = APIRouter()

router.include_router(cards_router)
router.include_router(notifications_router)
router.include_router(system_router)
