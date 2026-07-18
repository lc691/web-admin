"""
Portal Joki - Dashboard Quick Stats

Quick statistics endpoint.
"""

from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.dashboard.dashboard_service import (
    PortalJokiDashboardService,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/quick-stats",
    name="portal_joki_admin_dashboard_quick_stats",
)
async def quick_stats(
    request: Request,
):
    """
    Get quick statistics.
    """
    log.debug("Admin dashboard quick stats")

    try:
        require_admin(request)

        stats = PortalJokiDashboardService.get_admin_quick_stats()

        return JSONResponse(
            {
                "success": True,
                "data": stats,
                "generated_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        log.error(f"Failed to get quick stats: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )