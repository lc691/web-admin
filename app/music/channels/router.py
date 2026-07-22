"""
Channel Router
"""

from fastapi import APIRouter

from .page import router as page_router
from .routers.bulk import router as bulk_router
from .routers.crud import router as crud_router
from .routers.data import router as data_router
from .routers.statistics import router as statistics_router

router = APIRouter(
    prefix="/channels",
    tags=["Channels"],
)

# Halaman (Jinja2)
router.include_router(page_router)

# API
router.include_router(data_router)
router.include_router(statistics_router)
router.include_router(crud_router)
router.include_router(bulk_router)