"""
Portal Joki - Dashboard Chart Data

Chart data endpoint.
"""

from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.dashboard.dashboard_service import (
    PortalJokiDashboardService,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/chart-data",
    name="portal_joki_admin_dashboard_chart_data",
)
async def chart_data(
    request: Request,
    days: int = Query(
        30,
        ge=1,
        le=90,
        description="Number of days",
    ),
):
    """
    Get dashboard chart data.
    """
    log.info(f"Admin dashboard chart data: days={days}")

    try:
        require_admin(request)

        data = PortalJokiDashboardService.get_chart_data(days=days)

        return JSONResponse(
            {
                "success": True,
                "data": data,
                "days": days,
                "generated_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        log.error(f"Failed to get chart data: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )