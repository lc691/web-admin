"""
Portal Joki - Dashboard Summary

Dashboard summary endpoint.
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
    "/summary",
    name="portal_joki_admin_dashboard_summary",
)
async def summary(
    request: Request,
):
    """
    Get dashboard summary.
    """
    log.debug("Admin dashboard summary")

    try:
        require_admin(request)

        result = PortalJokiDashboardService.execute_admin()
        summary = result.summary or {}

        total = summary.get("total_penugasan", 0)
        completed = summary.get("selesai", 0)

        summary["completion_rate"] = round(
            (completed / max(total, 1)) * 100,
            2,
        )

        return JSONResponse(
            {
                "success": True,
                "data": summary,
                "generated_at": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        log.error(f"Failed to get dashboard summary: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )