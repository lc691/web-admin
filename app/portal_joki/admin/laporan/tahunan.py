"""
Portal Joki - Admin Laporan Tahunan Routes
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
    "/tahunan",
    name="portal_joki_admin_laporan_tahunan",
)
async def laporan_tahunan(
    request: Request,
    tahun: int = Query(
        ...,
        description="Tahun",
    ),
):
    """
    Get yearly summary.
    """
    log.info(f"Ringkasan tahunan: tahun={tahun}")

    try:
        require_admin(request)

        result = PortalJokiBulananService.get_yearly_summary(
            tahun=tahun,
        )

        return JSONResponse(
            {
                "success": True,
                "data": result,
                "tahun": tahun,
            }
        )

    except Exception as e:
        log.error(f"Failed to get yearly summary: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )