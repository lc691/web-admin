"""
Portal Joki - Admin Laporan Page Routes
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Query, Request

from app.templates import templates

from app.dependencies.auth import require_admin
from app.portal_joki.repositories.auth.auth_repo import (
    PortalJokiAuthRepository,
)
from app.portal_joki.services.laporan.bulanan import (
    PortalJokiBulananService,
)
from app.portal_joki.services.laporan.harian import (
    PortalJokiHarianService,
)
from app.portal_joki.services.laporan.statistik import (
    PortalJokiStatistikService,
)
from app.utils.logger import log

from .constants import (
    DEFAULT_VIEW,
    VALID_VIEWS,
)
from .helpers import (
    get_month_name,
    get_status_color,
    get_status_label,
    normalize_month,
    parse_date,
)

router = APIRouter()


@router.get(
    "/",
    name="portal_joki_admin_laporan",
)
async def laporan_page(
    request: Request,
    tahun: Optional[int] = Query(
        None,
        description="Tahun",
    ),
    bulan: Optional[int] = Query(
        None,
        description="Bulan",
    ),
    tanggal: Optional[str] = Query(
        None,
        description="Tanggal (YYYY-MM-DD)",
    ),
    view: str = Query(
        DEFAULT_VIEW,
        description="View laporan",
    ),
):
    """
    Halaman utama laporan Portal Joki.
    """
    log.info(
        "Admin laporan page: "
        f"tahun={tahun}, "
        f"bulan={bulan}, "
        f"tanggal={tanggal}, "
        f"view={view}"
    )

    now = datetime.now()
    today = now.date()

    try:
        admin = require_admin(request)

        if tahun is None:
            tahun = today.year

        bulan = normalize_month(
            bulan,
            today.month,
        )

        if view not in VALID_VIEWS:
            view = DEFAULT_VIEW

        # ======================================================
        # Statistik
        # ======================================================

        statistik_result = PortalJokiStatistikService.execute()

        statistik = (
            statistik_result.data
            if statistik_result.success
            else {}
        )

        # ======================================================
        # Bulanan
        # ======================================================

        bulanan_result = PortalJokiBulananService.execute(
            tahun=tahun,
            bulan=bulan,
        )

        if bulanan_result.success:
            bulanan = bulanan_result.data
            bulanan_stats = bulanan_result.stats
        else:
            bulanan = []
            bulanan_stats = {}

        # ======================================================
        # Harian
        # ======================================================

        harian = []
        harian_stats = {}

        tanggal_date = parse_date(tanggal)

        if tanggal_date:
            harian_result = PortalJokiHarianService.execute(
                tanggal_date
            )

            if harian_result.success:
                harian = harian_result.data
                harian_stats = harian_result.stats

        # ======================================================
        # Joki
        # ======================================================

        joki_list = PortalJokiAuthRepository.get_active()

        month_name = get_month_name(bulan)

        return templates.TemplateResponse(
            "portal_joki/admin/laporan/index.html",
            {
                "request": request,
                "title": "Laporan",

                "admin": admin,
                "view": view,

                # Filter
                "tahun": tahun,
                "bulan": bulan,
                "tanggal": tanggal,
                "month_name": month_name,

                # Data
                "statistik": statistik,

                "bulanan": bulanan,
                "bulanan_stats": bulanan_stats,

                "harian": harian,
                "harian_stats": harian_stats,

                "joki_list": joki_list,

                # Helper
                "get_month_name": get_month_name,
                "get_status_label": get_status_label,
                "get_status_color": get_status_color,

                # Datetime
                "generated_at": now,
                "now": datetime.now(),
            },
        )

    except Exception as e:
        log.error(f"Failed to load laporan page: {e}")

        return templates.TemplateResponse(
            "portal_joki/admin/laporan/index.html",
            {
                "request": request,
                "title": "Laporan",

                "error": str(e),

                "admin": None,
                "view": view,

                # Filter
                "tahun": tahun or today.year,
                "bulan": bulan,
                "tanggal": tanggal,
                "month_name": get_month_name(bulan),

                # Data kosong
                "statistik": {},

                "bulanan": [],
                "bulanan_stats": {},

                "harian": [],
                "harian_stats": {},

                "joki_list": [],

                # Helper
                "get_month_name": get_month_name,
                "get_status_label": get_status_label,
                "get_status_color": get_status_color,

                # Datetime
                "generated_at": now,
                "now": datetime.now(),
            },
        )