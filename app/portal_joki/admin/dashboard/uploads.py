"""
Portal Joki - Dashboard Uploads

Recent uploads endpoint.
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
    "/uploads",
    name="portal_joki_admin_dashboard_uploads",
)
async def uploads(
    request: Request,
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of uploads",
    ),
):
    """
    Get recent uploads.
    """
    log.info(f"Admin dashboard uploads: limit={limit}")

    try:
        require_admin(request)

        result = PortalJokiDashboardService.execute_admin()
        data = result.recent_uploads or []

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
        log.error(f"Failed to get uploads: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )