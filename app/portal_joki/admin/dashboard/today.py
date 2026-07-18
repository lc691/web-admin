"""
Portal Joki - Dashboard Today

Today's tasks endpoint.
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
    "/today",
    name="portal_joki_admin_dashboard_today",
)
async def today(
    request: Request,
):
    """
    Get today's tasks.
    """
    log.debug("Admin dashboard today tasks")

    try:
        require_admin(request)

        result = PortalJokiDashboardService.execute_admin()
        data = result.today or []

        status_map = {
            0: "Pending",
            1: "Upload",
            2: "Revisi",
            3: "Selesai",
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
                "generated_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        log.error(f"Failed to get today tasks: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )