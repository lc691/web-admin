"""
Portal Joki - Dashboard Latest Review

Latest review endpoint.
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
    "/latest-review",
    name="portal_joki_admin_dashboard_latest_review",
)
async def latest_review(
    request: Request,
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of reviews",
    ),
):
    """
    Get latest reviews.
    """
    log.info(f"Admin dashboard latest review: limit={limit}")

    try:
        require_admin(request)

        result = PortalJokiDashboardService.execute_admin()
        data = result.latest_review or []

        if limit and len(data) > limit:
            data = data[:limit]

        status_map = {
            1: "Approved",
            2: "Revision",
            3: "Rejected",
        }

        for item in data:
            item["status_label"] = status_map.get(
                item.get("status", 0),
                "Unknown",
            )

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
        log.error(f"Failed to get latest review: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )