from fastapi import APIRouter

from .dashboard import router as dashboard_router
from .calendar import router as calendar_router
from .holiday import router as holiday_router
from .penugasan import router as penugasan_router
from .review import router as review_router
from .laporan import router as laporan_router

router = APIRouter()

router.include_router(dashboard_router)
router.include_router(calendar_router)
router.include_router(holiday_router)
router.include_router(penugasan_router)
router.include_router(review_router)
router.include_router(laporan_router)