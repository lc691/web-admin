"""
Portal Joki - Laporan Helpers
"""

from __future__ import annotations

from datetime import date, datetime
from calendar import monthrange

from .constants import (
    MONTH_NAMES,
    STATUS_COLORS,
    STATUS_LABELS,
)


# ==========================================================
# MONTH
# ==========================================================

def get_month_name(month: int) -> str:
    """
    Mendapatkan nama bulan dalam Bahasa Indonesia.
    """
    return MONTH_NAMES[month - 1] if 1 <= month <= 12 else ""


def get_days_in_month(year: int, month: int) -> int:
    """
    Mendapatkan jumlah hari dalam bulan.
    """
    return monthrange(year, month)[1]


# ==========================================================
# STATUS
# ==========================================================

def get_status_label(status: int) -> str:
    """
    Mendapatkan label status.
    """
    return STATUS_LABELS.get(status, "Unknown")


def get_status_color(status: int) -> str:
    """
    Mendapatkan warna badge status.
    """
    return STATUS_COLORS.get(status, "secondary")


# ==========================================================
# DATE
# ==========================================================

def parse_date(value: str | None) -> date | None:
    """
    Parse string YYYY-MM-DD menjadi date.
    """
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def format_date(value: date | datetime | None) -> str:
    """
    Format date/datetime menjadi YYYY-MM-DD.
    """
    if value is None:
        return ""

    if isinstance(value, datetime):
        value = value.date()

    return value.strftime("%Y-%m-%d")


# ==========================================================
# VALIDATION
# ==========================================================

def normalize_month(month: int | None, default: int) -> int:
    """
    Memastikan bulan berada pada rentang 1-12.
    """
    if month is None:
        return default

    return month if 1 <= month <= 12 else default