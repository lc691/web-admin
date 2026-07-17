"""
Portal Joki - Admin Laporan Bulanan Routes
"""

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.laporan.bulanan import (
    PortalJokiBulananService,
)
from app.portal_joki.admin.laporan.helpers import (
    get_month_name,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/bulanan",
    name="portal_joki_admin_laporan_bulanan",
)
async def laporan_bulanan(
    request: Request,
    tahun: int = Query(..., description="Tahun"),
    bulan: int = Query(..., description="Bulan"),
):
    """
    Get monthly report.
    """
    log.info(f"Laporan bulanan: tahun={tahun}, bulan={bulan}")

    try:
        require_admin(request)

        if not 1 <= bulan <= 12:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Bulan tidak valid. (1-12)",
                },
                status_code=400,
            )

        result = PortalJokiBulananService.execute(
            tahun=tahun,
            bulan=bulan,
        )

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
                "tahun": tahun,
                "bulan": bulan,
                "month_name": get_month_name(bulan),
            }
        )

    except Exception as e:
        log.error(f"Failed to get monthly report: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )