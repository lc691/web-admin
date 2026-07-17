from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates import templates

from .repositories.dashboard.dashboard_repo import RekapDashboard


router = APIRouter(
    prefix="/laporan/dashboard",
    tags=["Dashboard Catatan"],
)


# ==========================================================
# DASHBOARD
# ==========================================================

@router.get(
    "",
    response_class=HTMLResponse,
)
def index(
    request: Request,
):

    return templates.TemplateResponse(
        "laporan/dashboard.html",
        {
            "request": request,
            "title": "Dashboard Catatan",

            # Ringkasan
            "summary": RekapDashboard.get_dashboard_summary(),

            # Hari ini
            "today": RekapDashboard.get_dashboard_today(),

            # Grafik 7 hari
            "week": RekapDashboard.get_dashboard_week(),

            # Top 5 Joki
            "top_joki": RekapDashboard.get_dashboard_top_joki(),

            # Top 5 Kloter
            "top_kloter": RekapDashboard.get_dashboard_top_kloter(),
        },
    )