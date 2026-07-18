"""
Portal Joki - Dashboard Routes
"""

from fastapi import APIRouter

from .page import router as page_router
from .data import router as data_router
from .summary import router as summary_router
from .today import router as today_router
from .uploads import router as uploads_router
from .top_joki import router as top_joki_router
from .latest_review import router as latest_review_router
from .quick_stats import router as quick_stats_router
from .chart_data import router as chart_data_router
from .refresh import router as refresh_router

router = APIRouter(
    prefix="/admin/portal-joki/dashboard",
    tags=["Portal Joki Admin"],
)

router.include_router(page_router)
router.include_router(data_router)
router.include_router(summary_router)
router.include_router(today_router)
router.include_router(uploads_router)
router.include_router(top_joki_router)
router.include_router(latest_review_router)
router.include_router(quick_stats_router)
router.include_router(chart_data_router)
router.include_router(refresh_router)

__all__ = ["router"]