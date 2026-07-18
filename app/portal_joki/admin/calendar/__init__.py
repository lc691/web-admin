"""
Portal Joki - Admin Calendar Routes
"""

from fastapi import APIRouter

from .page import router as page_router
from .day import router as day_router
from .data import router as data_router
from .week import router as week_router
from .stats import router as stats_router
from .holidays import router as holidays_router

router = APIRouter(
    prefix="/admin/portal-joki/calendar",
    tags=["Portal Joki Admin"],
)

router.include_router(page_router)
router.include_router(day_router)
router.include_router(data_router)
router.include_router(week_router)
router.include_router(stats_router)
router.include_router(holidays_router)

__all__ = ["router"]