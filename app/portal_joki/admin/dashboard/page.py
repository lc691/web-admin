"""
Portal Joki - Admin Dashboard Page

Dashboard utama.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Query
from app.templates import templates

from app.dependencies.auth import require_admin
from app.portal_joki.services.dashboard.dashboard_service import (
    PortalJokiDashboardService,
)
from .helpers import format_dashboard_result, format_calendar_data
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/",
    name="portal_joki_admin_dashboard",
)
async def dashboard(
    request: Request,
    refresh: bool = Query(False, description="Force refresh data"),
):
    """
    Admin dashboard page.
    """
    log.info(f"Admin dashboard page: refresh={refresh}")

    try:
        admin = require_admin(request)
        
        # Get dashboard data
        result = PortalJokiDashboardService.execute_admin()
        data = format_dashboard_result(result)

        # Format calendar dengan posisi yang benar
        calendar_formatted = format_calendar_data(data.get("calendar", []))

        # Calculate additional stats
        summary = data["summary"]
        progress = data["progress"]
        
        stats = {
            "total_tasks": summary.get("total_penugasan", 0),
            "completed": summary.get("selesai", 0),
            "pending": summary.get("pending", 0),
            "revision": summary.get("revisi", 0),
            "total_joki": summary.get("total_joki", 0),
            "completion_rate": progress.get("persen", 0.0),
            "today_tasks": len(data["today"]),
            "total_uploads": len(data["recent_uploads"]),
        }

        return templates.TemplateResponse(
            "portal_joki/admin/dashboard/index.html",
            {
                "request": request,
                "title": "Dashboard Portal Joki",
                "admin": admin,
                "stats": stats,
                "summary": data["summary"],
                "today": data["today"],
                "calendar": calendar_formatted,
                "recent_uploads": data["recent_uploads"],
                "progress": data["progress"],
                "top_joki": data["top_joki"],
                "latest_review": data["latest_review"],
                "weekly_stats": data["weekly_stats"],
                "additional_data": data["additional_data"],
                "generated_at": datetime.now(),
                "refresh": refresh,
                "now": datetime.now(),  # ← Tambahkan ini
            },
        )

    except Exception as e:
        log.error(f"Failed to load admin dashboard: {e}")
        return templates.TemplateResponse(
            "portal_joki/admin/dashboard/index.html",
            {
                "request": request,
                "title": "Dashboard Portal Joki",
                "error": str(e),
                "stats": {},
                "summary": {},
                "progress": {},
                "today": [],
                "calendar": [],
                "recent_uploads": [],
                "top_joki": [],
                "latest_review": [],
                "weekly_stats": {},
                "additional_data": {},
                "generated_at": datetime.now(),
                "refresh": False,
                "now": datetime.now(),  # ← Tambahkan ini
            },
        )