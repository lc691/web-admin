from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.dependencies.auth import (
    get_current_joki,
)

from app.portal_joki.services.dashboard.dashboard_service import (
    PortalJokiDashboardService,
)


router = APIRouter(
    prefix="/portal-joki",
    tags=["Portal Joki Dashboard"],
)

templates = Jinja2Templates(
    directory="app/portal_joki/templates"
)


# ==========================================================
# DASHBOARD
# ==========================================================

@router.get(
    "/dashboard",
    name="portal_joki_dashboard",
)
async def dashboard(
    request: Request,
    user=Depends(get_current_joki),
):

    result = PortalJokiDashboardService.execute(
        joki_id=user["id"],
    )

    return templates.TemplateResponse(
        "portal_joki/dashboard.html",
        {
            "request": request,
            "title": "Dashboard",

            "user": user,

            "summary": result.summary,

            "today": result.today,

            "calendar": result.calendar,

            "recent_uploads": result.recent_uploads,

            "progress": result.progress,
        },
    )


# ==========================================================
# DASHBOARD DATA (AJAX)
# ==========================================================

@router.get(
    "/dashboard/data",
    name="portal_joki_dashboard_data",
)
async def dashboard_data(
    user=Depends(get_current_joki),
):

    result = PortalJokiDashboardService.execute(
        joki_id=user["id"],
    )

    return {
        "success": True,

        "summary": result.summary,

        "today": result.today,

        "calendar": result.calendar,

        "recent_uploads": result.recent_uploads,

        "progress": result.progress,
    }