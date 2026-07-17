"""
Portal Joki - Admin Laporan Routes
"""

from fastapi import APIRouter

from .page import router as page_router
from .harian import router as harian_router
from .bulanan import router as bulanan_router
from .statistik import router as statistik_router
from .rekap import router as rekap_router
from .trend import router as trend_router
from .tahunan import router as tahunan_router
from .perbandingan import router as perbandingan_router
from .export import router as export_router

router = APIRouter(
    prefix="/admin/portal-joki/laporan",
    tags=["Portal Joki Admin"],
)

router.include_router(page_router)
router.include_router(harian_router)
router.include_router(bulanan_router)
router.include_router(statistik_router)
router.include_router(rekap_router)
router.include_router(trend_router)
router.include_router(tahunan_router)
router.include_router(perbandingan_router)
router.include_router(export_router)