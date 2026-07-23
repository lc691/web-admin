"""
Channel Router - Complete Implementation

Main router untuk Channel dengan:
- Page routes (Jinja2 templates)
- API routes (JSON responses)
- CRUD operations
- Bulk operations
- Statistics endpoints
- DataTable endpoints
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

# Page routes (Jinja2 templates)
router.include_router(page_router)

# API routes (JSON responses)
router.include_router(data_router)
router.include_router(statistics_router)
router.include_router(crud_router)
router.include_router(bulk_router)

# Export router
__all__ = ['router']