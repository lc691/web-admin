"""
Portal Joki - Dashboard Refresh

Dashboard refresh endpoint.
"""

from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.dashboard.dashboard_service import (
    PortalJokiDashboardService,
)
from app.utils.logger import log

from .helpers import format_dashboard_result

router = APIRouter()


@router.post(
    "/refresh",
    name="portal_joki_admin_dashboard_refresh",
)
async def refresh(
    request: Request,
):
    """
    Refresh dashboard data.
    """
    log.info("Admin dashboard refresh")

    try:
        require_admin(request)

        result = PortalJokiDashboardService.execute_admin()
        data = format_dashboard_result(result)

        return JSONResponse(
            {
                "success": True,
                "message": "Dashboard data refreshed.",
                "data": data,
                "generated_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        log.error(f"Failed to refresh dashboard: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )