"""
Portal Joki - Admin Laporan Perbandingan Routes
"""

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.laporan.bulanan import (
    PortalJokiBulananService,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/perbandingan",
    name="portal_joki_admin_laporan_perbandingan",
)
async def laporan_perbandingan(
    request: Request,
    tahun1: int = Query(
        ...,
        description="Tahun pertama",
    ),
    bulan1: int = Query(
        ...,
        description="Bulan pertama",
    ),
    tahun2: int = Query(
        ...,
        description="Tahun kedua",
    ),
    bulan2: int = Query(
        ...,
        description="Bulan kedua",
    ),
):
    """
    Get comparison between two months.
    """
    log.info(
        f"Perbandingan: {tahun1}-{bulan1} vs {tahun2}-{bulan2}"
    )

    try:
        require_admin(request)

        if not 1 <= bulan1 <= 12:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Bulan pertama tidak valid. (1-12)",
                },
                status_code=400,
            )

        if not 1 <= bulan2 <= 12:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Bulan kedua tidak valid. (1-12)",
                },
                status_code=400,
            )

        result = PortalJokiBulananService.get_comparison(
            tahun1=tahun1,
            bulan1=bulan1,
            tahun2=tahun2,
            bulan2=bulan2,
        )

        return JSONResponse(
            {
                "success": True,
                "data": result,
                "periode_1": {
                    "tahun": tahun1,
                    "bulan": bulan1,
                },
                "periode_2": {
                    "tahun": tahun2,
                    "bulan": bulan2,
                },
            }
        )

    except Exception as e:
        log.error(f"Failed to get comparison: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )