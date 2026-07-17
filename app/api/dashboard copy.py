from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime, timedelta

from app.utils.logger import log
from app.core.database import get_db_cursor
from app.templates import templates
from app.base.routes import get_dashboard_stats

router = APIRouter(tags=["dashboard"])


# =========================
# MAIN DASHBOARD
# =========================
@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    stats = get_dashboard_stats()

    chart_labels = stats.get("chart_labels", [])
    chart_data = stats.get("chart_data", [])
    revenue_distribution = stats.get("revenue_distribution", [0, 0, 0])
    recent_activities = stats.get("recent_activities", [])
    top_shows = stats.get("top_shows", [])

    is_ajax = request.headers.get(
        "X-Requested-With"
    ) == "XMLHttpRequest" or request.query_params.get("ajax")

    if is_ajax:
        return JSONResponse(
            {
                "stats": stats,
                "chart_labels": chart_labels,
                "chart_data": chart_data,
                "revenue_distribution": revenue_distribution,
                "recent_activities": recent_activities,
                "top_shows": top_shows,
            }
        )

    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "stats": stats,
            "chart_labels": chart_labels,
            "chart_data": chart_data,
            "revenue_distribution": revenue_distribution,
            "recent_activities": recent_activities,
            "top_shows": top_shows,
        },
    )


# =========================
# CHART API
# =========================
@router.get("/api/dashboard/chart")
async def dashboard_chart(period: int = 30):
    """API endpoint for VIP chart data"""
    try:
        interval_days = max(1, min(period, 90))  # clamp 1–90 days

        with get_db_cursor() as (cursor, _):
            cursor.execute(
                """
                SELECT 
                    DATE(created_at) AS date,
                    COUNT(*) AS vip_count
                FROM users
                WHERE is_vip = true
                  AND created_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
                """,
                (interval_days,),
            )

            rows = cursor.fetchall()
            data_map = {row[0]: row[1] for row in rows if row[0]}

        today = datetime.now().date()

        labels = []
        values = []

        for i in range(interval_days, -1, -1):
            d = today - timedelta(days=i)
            labels.append(d.strftime("%d %b"))
            values.append(data_map.get(d, 0))

        log.info(f"[Dashboard Chart] period={interval_days}, points={len(values)}")

        return JSONResponse(
            {
                "labels": labels,
                "values": values,
            }
        )

    except Exception as e:
        log.error(f"[Dashboard Chart Error] {e}", exc_info=True)
        return JSONResponse(
            {
                "labels": [],
                "values": [],
                "error": str(e),
            },
            status_code=500,
        )
