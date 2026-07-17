"""
Portal Joki - Admin Dashboard Routes

Routes untuk dashboard admin portal joki.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from app.templates import templates

from app.dependencies.auth import require_admin
from app.portal_joki.services.dashboard.dashboard_service import (
    PortalJokiDashboardService,
)
from app.utils.logger import log

# ==========================================================
# ROUTER & TEMPLATES
# ==========================================================
router = APIRouter(
    prefix="/admin/portal-joki/dashboard",
    tags=["Portal Joki Admin"],
)


# ==========================================================
# HELPER
# ==========================================================
def _format_dashboard_result(result):
    """Format dashboard result untuk template."""
    return {
        "summary": result.summary or {},
        "today": result.today or [],
        "calendar": result.calendar or [],
        "recent_uploads": result.recent_uploads or [],
        "progress": result.progress or {},
        "top_joki": result.top_joki or [],
        "latest_review": result.latest_review or [],
        "weekly_stats": result.weekly_stats or {},
        "additional_data": result.additional_data or {},
    }


# ==========================================================
# DASHBOARD PAGE
# ==========================================================
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
        data = _format_dashboard_result(result)

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
            "portal_joki/admin/dashboard.html",
            {
                "request": request,
                "title": "Dashboard Portal Joki",
                "admin": admin,

                "stats": stats,

                "summary": data["summary"],
                "today": data["today"],
                "calendar": data["calendar"],
                "recent_uploads": data["recent_uploads"],
                "progress": data["progress"],
                "top_joki": data["top_joki"],
                "latest_review": data["latest_review"],
                "weekly_stats": data["weekly_stats"],
                "additional_data": data["additional_data"],

                "generated_at": datetime.now(),
                "refresh": refresh,
            },
        )

    except Exception as e:
        log.error(f"Failed to load admin dashboard: {e}")
        return templates.TemplateResponse(
            "portal_joki/admin/dashboard.html",
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
            },
        )


# ==========================================================
# DASHBOARD DATA (JSON)
# ==========================================================
@router.get(
    "/data",
    name="portal_joki_admin_dashboard_data",
)
async def dashboard_data(
    request: Request,
    refresh: bool = Query(False, description="Force refresh data"),
):
    """
    Get dashboard data as JSON.
    """
    log.info(f"Admin dashboard data: refresh={refresh}")

    try:
        require_admin(request)
        
        result = PortalJokiDashboardService.execute_admin()
        data = _format_dashboard_result(result)

        return JSONResponse({
            "success": True,
            "data": data,
            "generated_at": datetime.now().isoformat(),
            "refresh": refresh,
        })

    except Exception as e:
        log.error(f"Failed to get dashboard data: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "generated_at": datetime.now().isoformat(),
        }, status_code=500)


# ==========================================================
# SUMMARY
# ==========================================================
@router.get(
    "/summary",
    name="portal_joki_admin_dashboard_summary",
)
async def summary(
    request: Request,
):
    """
    Get dashboard summary as JSON.
    """
    log.debug("Admin dashboard summary")

    try:
        require_admin(request)
        
        result = PortalJokiDashboardService.execute_admin()
        summary = result.summary or {}

        # Add completion rate
        total = summary.get("total_penugasan", 0)
        completed = summary.get("selesai", 0)
        summary["completion_rate"] = round((completed / max(total, 1)) * 100, 2)

        return JSONResponse({
            "success": True,
            "data": summary,
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to get summary: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# TODAY TASKS
# ==========================================================
@router.get(
    "/today",
    name="portal_joki_admin_dashboard_today",
)
async def today(
    request: Request,
):
    """
    Get today's tasks as JSON.
    """
    log.debug("Admin dashboard today tasks")

    try:
        require_admin(request)
        
        result = PortalJokiDashboardService.execute_admin()
        today_data = result.today or []

        # Add status labels
        status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
        for item in today_data:
            item["status_label"] = status_map.get(item.get("status", 0), "Unknown")

        return JSONResponse({
            "success": True,
            "data": today_data,
            "total": len(today_data),
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to get today tasks: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# RECENT UPLOADS
# ==========================================================
@router.get(
    "/uploads",
    name="portal_joki_admin_dashboard_uploads",
)
async def uploads(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="Number of uploads"),
):
    """
    Get recent uploads as JSON.
    """
    log.info(f"Admin dashboard uploads: limit={limit}")

    try:
        require_admin(request)
        
        result = PortalJokiDashboardService.execute_admin()
        uploads_data = result.recent_uploads or []

        # Limit results
        if limit and len(uploads_data) > limit:
            uploads_data = uploads_data[:limit]

        return JSONResponse({
            "success": True,
            "data": uploads_data,
            "total": len(uploads_data),
            "limit": limit,
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to get uploads: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# TOP JOKI
# ==========================================================
@router.get(
    "/top-joki",
    name="portal_joki_admin_dashboard_top_joki",
)
async def top_joki(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Number of top joki"),
):
    """
    Get top joki as JSON.
    """
    log.info(f"Admin dashboard top joki: limit={limit}")

    try:
        require_admin(request)
        
        result = PortalJokiDashboardService.execute_admin()
        top_joki_data = result.top_joki or []

        # Limit results
        if limit and len(top_joki_data) > limit:
            top_joki_data = top_joki_data[:limit]

        return JSONResponse({
            "success": True,
            "data": top_joki_data,
            "total": len(top_joki_data),
            "limit": limit,
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to get top joki: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# LATEST REVIEW
# ==========================================================
@router.get(
    "/latest-review",
    name="portal_joki_admin_dashboard_latest_review",
)
async def latest_review(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="Number of reviews"),
):
    """
    Get latest reviews as JSON.
    """
    log.info(f"Admin dashboard latest review: limit={limit}")

    try:
        require_admin(request)
        
        result = PortalJokiDashboardService.execute_admin()
        reviews_data = result.latest_review or []

        # Limit results
        if limit and len(reviews_data) > limit:
            reviews_data = reviews_data[:limit]

        # Add status labels
        status_map = {1: "Approved", 2: "Revision", 3: "Rejected"}
        for item in reviews_data:
            item["status_label"] = status_map.get(item.get("status", 0), "Unknown")

        return JSONResponse({
            "success": True,
            "data": reviews_data,
            "total": len(reviews_data),
            "limit": limit,
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to get latest review: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# QUICK STATS
# ==========================================================
@router.get(
    "/quick-stats",
    name="portal_joki_admin_dashboard_quick_stats",
)
async def quick_stats(
    request: Request,
):
    """
    Get quick stats as JSON.
    """
    log.debug("Admin dashboard quick stats")

    try:
        require_admin(request)
        
        stats = PortalJokiDashboardService.get_admin_quick_stats()

        return JSONResponse({
            "success": True,
            "data": stats,
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to get quick stats: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# CHART DATA
# ==========================================================
@router.get(
    "/chart-data",
    name="portal_joki_admin_dashboard_chart_data",
)
async def chart_data(
    request: Request,
    days: int = Query(30, ge=1, le=90, description="Number of days"),
):
    """
    Get chart data as JSON.
    """
    log.info(f"Admin dashboard chart data: days={days}")

    try:
        require_admin(request)
        
        chart_data = PortalJokiDashboardService.get_chart_data(days=days)

        return JSONResponse({
            "success": True,
            "data": chart_data,
            "days": days,
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to get chart data: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# REFRESH
# ==========================================================
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
        
        # Force refresh by getting fresh data
        result = PortalJokiDashboardService.execute_admin()
        data = _format_dashboard_result(result)

        return JSONResponse({
            "success": True,
            "message": "Dashboard data refreshed.",
            "data": data,
            "generated_at": datetime.now().isoformat(),
        })

    except Exception as e:
        log.error(f"Failed to refresh dashboard: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)