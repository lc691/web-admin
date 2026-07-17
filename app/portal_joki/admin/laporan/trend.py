"""
Portal Joki - Admin Laporan Trend Routes
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
    "/trend",
    name="portal_joki_admin_laporan_trend",
)
async def laporan_trend(
    request: Request,
    joki_id: int | None = Query(
        None,
        description="ID Joki",
    ),
    months: int = Query(
        6,
        description="Jumlah bulan",
        ge=1,
        le=24,
    ),
):
    """
    Get performance trend.
    """
    log.info(f"Trend: joki_id={joki_id}, months={months}")

    try:
        require_admin(request)

        result = PortalJokiBulananService.get_trend(
            joki_id=joki_id,
            months=months,
        )

        return JSONResponse(
            {
                "success": True,
                "data": result,
                "joki_id": joki_id,
                "months": months,
            }
        )

    except Exception as e:
        log.error(f"Failed to get trend: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )