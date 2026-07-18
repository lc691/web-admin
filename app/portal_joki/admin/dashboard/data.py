"""
Portal Joki - Dashboard Data

Dashboard JSON data endpoint.
"""

from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.dashboard.dashboard_service import (
    PortalJokiDashboardService,
)
from app.utils.logger import log

from .helpers import format_dashboard_result

router = APIRouter()


@router.get(
    "/data",
    name="portal_joki_admin_dashboard_data",
)
async def dashboard_data(
    request: Request,
    refresh: bool = Query(
        False,
        description="Force refresh data",
    ),
):
    """
    Get dashboard data.
    """
    log.info(f"Admin dashboard data: refresh={refresh}")

    try:
        require_admin(request)

        result = PortalJokiDashboardService.execute_admin()
        data = format_dashboard_result(result)

        return JSONResponse(
            {
                "success": True,
                "data": data,
                "generated_at": datetime.now().isoformat(),
                "refresh": refresh,
            }
        )

    except Exception as e:
        log.error(f"Failed to get dashboard data: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
            },
            status_code=500,
        )