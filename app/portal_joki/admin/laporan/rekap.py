"""
Portal Joki - Admin Laporan Rekap Bulanan Routes
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
    "/rekap-bulanan",
    name="portal_joki_admin_laporan_rekap_bulanan",
)
async def rekap_bulanan(
    request: Request,
    tahun: int = Query(..., description="Tahun"),
    bulan: int = Query(..., description="Bulan"),
):
    """
    Get monthly recap.
    """
    log.info(f"Rekap bulanan: tahun={tahun}, bulan={bulan}")

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

        result = PortalJokiBulananService.get_rekap(
            tahun=tahun,
            bulan=bulan,
        )

        return JSONResponse(
            {
                "success": True,
                "data": result,
                "tahun": tahun,
                "bulan": bulan,
            }
        )

    except Exception as e:
        log.error(f"Failed to get monthly recap: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )