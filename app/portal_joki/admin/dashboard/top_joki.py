"""
Portal Joki - Dashboard Top Joki

Top joki endpoint.
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
    "/top-joki",
    name="portal_joki_admin_dashboard_top_joki",
)
async def top_joki(
    request: Request,
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Number of top joki",
    ),
):
    """
    Get top joki.
    """
    log.info(f"Admin dashboard top joki: limit={limit}")

    try:
        require_admin(request)

        result = PortalJokiDashboardService.execute_admin()
        data = result.top_joki or []

        if limit and len(data) > limit:
            data = data[:limit]

        return JSONResponse(
            {
                "success": True,
                "data": data,
                "total": len(data),
                "limit": limit,
                "generated_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        log.error(f"Failed to get top joki: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )