"""
Portal Joki - Admin Laporan Statistik Routes
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.laporan.statistik import (
    PortalJokiStatistikService,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/statistik",
    name="portal_joki_admin_laporan_statistik",
)
async def laporan_statistik(
    request: Request,
):
    """
    Get statistics report.
    """
    log.info("Laporan statistik")

    try:
        require_admin(request)

        result = PortalJokiStatistikService.execute()

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
            }
        )

    except Exception as e:
        log.error(f"Failed to get statistics: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )