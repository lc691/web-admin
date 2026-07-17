"""
Portal Joki - Admin Laporan Harian Routes
"""

from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.laporan.harian import (
    PortalJokiHarianService,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/harian",
    name="portal_joki_admin_laporan_harian",
)
async def laporan_harian(
    request: Request,
    tanggal: str = Query(..., description="Tanggal (YYYY-MM-DD)"),
):
    """
    Get daily report.
    """
    log.info(f"Laporan harian: tanggal={tanggal}")

    try:
        require_admin(request)

        try:
            tanggal_date = datetime.strptime(
                tanggal,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
                },
                status_code=400,
            )

        result = PortalJokiHarianService.execute(tanggal_date)

        if not result.success:
            return JSONResponse(
                {
                    "success": False,
                    "error": result.message,
                },
                status_code=400,
            )

        return JSONResponse(
            {
                "success": True,
                "data": result.data,
                "stats": result.stats,
                "tanggal": tanggal,
            }
        )

    except Exception as e:
        log.error(f"Failed to get daily report: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )