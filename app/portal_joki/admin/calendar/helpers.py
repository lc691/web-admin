"""
Portal Joki - Calendar Helpers
"""

from calendar import monthrange
from datetime import date, datetime
from typing import Any, Dict, List, Optional


def get_month_name(month: int) -> str:
    """Get month name in Indonesian."""
    months = [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    return months[month - 1] if 1 <= month <= 12 else ""


def safe_get(data: Any, key: str, default=0):
    """Safe get from dict or return default."""
    if isinstance(data, dict):
        return data.get(key, default)
    return default


def extract_holidays(result) -> List[Dict[str, Any]]:
    """
    Extract holiday data safely.
    """
    holidays_data = []

    if result.success and result.data:
        if isinstance(result.data, dict):
            holidays_data = result.data.get("data", [])
        elif isinstance(result.data, list):
            holidays_data = result.data
        else:
            holidays_data = []

    return holidays_data


def parse_date(date_str: str) -> date:
    """
    Parse YYYY-MM-DD string to date.
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def serialize_data(data: List[Any]) -> List[Any]:
    """
    Convert objects to JSON serializable format.
    """
    serialized_data = []

    for item in data:
        if isinstance(item, dict):
            serializable_item = {}

            for key, value in item.items():
                if isinstance(value, (date, datetime)):
                    serializable_item[key] = value.isoformat()
                elif hasattr(value, "isoformat"):
                    serializable_item[key] = value.isoformat()
                else:
                    serializable_item[key] = value

            serialized_data.append(serializable_item)

        elif isinstance(item, (list, tuple)):
            serialized_item = []

            for value in item:
                if isinstance(value, (date, datetime)):
                    serialized_item.append(value.isoformat())
                elif hasattr(value, "isoformat"):
                    serialized_item.append(value.isoformat())
                else:
                    serialized_item.append(value)

            serialized_data.append(serialized_item)

        else:
            serialized_data.append(item)

    return serialized_data


def build_calendar_data(
    year: int,
    month: int,
    calendar_data: List[Dict[str, Any]],
    holidays: List[Dict[str, Any]],
) -> List[List[Optional[Dict[str, Any]]]]:
    """
    Build calendar grid data.
    """
    first_day = date(year, month, 1)
    last_day = monthrange(year, month)[1]

    start_weekday = first_day.weekday() + 1
    if start_weekday == 7:
        start_weekday = 0

    calendar_dict = {}

    for day in calendar_data:
        if isinstance(day, dict):
            tanggal = day.get("tanggal")
            if tanggal:
                if hasattr(tanggal, "strftime"):
                    date_str = tanggal.strftime("%Y-%m-%d")
                else:
                    date_str = str(tanggal)

                calendar_dict[date_str] = day

        elif isinstance(day, (list, tuple)):
            if len(day) >= 9:
                tanggal = day[0]

                if hasattr(tanggal, "strftime"):
                    date_str = tanggal.strftime("%Y-%m-%d")
                else:
                    date_str = str(tanggal)

                calendar_dict[date_str] = {
                    "tanggal": tanggal,
                    "total": day[1] if len(day) > 1 else 0,
                    "total_joki": day[2] if len(day) > 2 else 0,
                    "total_kloter": day[3] if len(day) > 3 else 0,
                    "total_target": day[4] if len(day) > 4 else 0,
                    "pending": day[5] if len(day) > 5 else 0,
                    "upload": day[6] if len(day) > 6 else 0,
                    "revisi": day[7] if len(day) > 7 else 0,
                    "selesai": day[8] if len(day) > 8 else 0,
                }

    holiday_set = set()

    for holiday in holidays:
        if not isinstance(holiday, dict):
            continue

        tanggal = holiday.get("tanggal")

        if tanggal:
            if hasattr(tanggal, "strftime"):
                date_str = tanggal.strftime("%Y-%m-%d")
            else:
                date_str = str(tanggal)

            holiday_set.add(date_str)

    grid = []
    today = date.today()

    week = []

    for _ in range(start_weekday):
        week.append(None)

    for day_num in range(1, last_day + 1):
        current_date = date(year, month, day_num)
        date_str = current_date.strftime("%Y-%m-%d")

        day_data = calendar_dict.get(date_str, {})

        cell = {
            "day": day_num,
            "date": date_str,
            "is_today": current_date == today,
            "is_holiday": date_str in holiday_set,
            "total_tasks": safe_get(day_data, "total", 0),
            "pending": safe_get(day_data, "pending", 0),
            "upload": safe_get(day_data, "upload", 0),
            "revisi": safe_get(day_data, "revisi", 0),
            "selesai": safe_get(day_data, "selesai", 0),
            "tasks": [],
        }

        week.append(cell)

        if len(week) == 7:
            grid.append(week)
            week = []

    if week:
        while len(week) < 7:
            week.append(None)

        grid.append(week)

    return grid