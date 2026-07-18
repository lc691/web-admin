"""
Portal Joki - Admin Calendar Page
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Query, Request

from app.dependencies.auth import require_admin
from app.portal_joki.services.calendar.calendar_service import (
    PortalJokiCalendarService,
)
from app.templates import templates
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/",
    name="portal_joki_admin_calendar",
)
async def calendar_page(
    request: Request,
    year: Optional[int] = Query(None, description="Tahun"),
    month: Optional[int] = Query(None, description="Bulan"),
    today: bool = Query(False, description="Buka hari ini"),
):
    """
    Admin calendar page.
    """
    log.info(
        f"Admin calendar page: year={year}, month={month}, today={today}"
    )

    try:
        admin = require_admin(request)

        now = date.today()

        if today:
            year = now.year
            month = now.month
        else:
            year = year or now.year
            month = month or now.month

            if not 1 <= month <= 12:
                year = now.year
                month = now.month

        result = PortalJokiCalendarService.month_admin(
            tahun=year,
            bulan=month,
        )

        return templates.TemplateResponse(
            "portal_joki/admin/calendar/index.html",
            {
                "request": request,
                "title": "Kalender Portal Joki",
                "admin": admin,

                "year": result.tahun,
                "month": result.bulan,
                "month_name": result.month_name,

                "calendar_data": result.calendar,
                "holidays": result.holidays,
                "stats": result.stats,

                "generated_at": datetime.now(),
            },
        )

    except Exception as e:
        log.exception(
            "Failed to load admin calendar page"
        )

        now = date.today()

        return templates.TemplateResponse(
            "portal_joki/admin/calendar/index.html",
            {
                "request": request,
                "title": "Kalender Portal Joki",

                "error": str(e),

                "year": now.year,
                "month": now.month,
                "month_name": now.strftime("%B"),

                "calendar_data": [],
                "holidays": [],
                "stats": {},

                "generated_at": datetime.now(),
            },
        )