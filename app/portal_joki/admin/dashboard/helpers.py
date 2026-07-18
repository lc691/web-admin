"""
Portal Joki - Admin Helpers

Helper functions untuk admin dashboard.
"""

from datetime import date
from calendar import monthrange
from typing import Dict, Any, List
from app.utils.logger import log


def format_dashboard_result(result):
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


def format_calendar_data(calendar_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format calendar data dengan posisi hari yang benar (Indonesia).
    """
    if not calendar_raw:
        log.warning("Calendar raw data is empty")
        return []
    
    try:
        today = date.today()
        year = today.year
        month = today.month
        
        # Python: 0 = Monday, 6 = Sunday
        # Indonesia: 0 = Sunday, 6 = Saturday
        first_day = date(year, month, 1)
        start_weekday = (first_day.weekday() + 1) % 7
        
        log.info(f"Format calendar: year={year}, month={month}, start_weekday={start_weekday}")
        log.info(f"Calendar raw: {calendar_raw}")
        
        # Convert raw data to dict by day
        calendar_dict = {}
        for item in calendar_raw:
            # Cek apakah item adalah dict atau tuple
            if isinstance(item, dict):
                tanggal = item.get("tanggal")
                if tanggal and hasattr(tanggal, "day"):
                    day_num = tanggal.day
                    calendar_dict[day_num] = {
                        "day": day_num,
                        "tanggal": tanggal,
                        "total": item.get("total", 0),
                        "pending": item.get("pending", 0),
                        "upload": item.get("upload", 0),
                        "revisi": item.get("revisi", 0),
                        "selesai": item.get("selesai", 0),
                        "is_holiday": False,
                    }
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                # Jika data berupa tuple/list: (tanggal, total, ...)
                tanggal = item[0]
                if hasattr(tanggal, "day"):
                    day_num = tanggal.day
                    calendar_dict[day_num] = {
                        "day": day_num,
                        "tanggal": tanggal,
                        "total": item[1] if len(item) > 1 else 0,
                        "pending": item[2] if len(item) > 2 else 0,
                        "upload": item[3] if len(item) > 3 else 0,
                        "revisi": item[4] if len(item) > 4 else 0,
                        "selesai": item[5] if len(item) > 5 else 0,
                        "is_holiday": False,
                    }
        
        log.info(f"Calendar dict: {calendar_dict}")
        
        # Build calendar grid
        calendar_grid = []
        
        # Add empty cells at beginning
        for _ in range(start_weekday):
            calendar_grid.append(None)
        
        # Add all days of month
        last_day = monthrange(year, month)[1]
        for day_num in range(1, last_day + 1):
            if day_num in calendar_dict:
                calendar_grid.append(calendar_dict[day_num])
            else:
                calendar_grid.append({
                    "day": day_num,
                    "tanggal": f"{year}-{month:02d}-{day_num:02d}",
                    "total": 0,
                    "pending": 0,
                    "upload": 0,
                    "revisi": 0,
                    "selesai": 0,
                    "is_holiday": False,
                })
        
        # Pad end of month
        while len(calendar_grid) % 7 != 0:
            calendar_grid.append(None)
        
        log.info(f"Calendar grid length: {len(calendar_grid)}")
        return calendar_grid
        
    except Exception as e:
        log.error(f"Error formatting calendar: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_status_label(status: int) -> str:
    """Get status label."""
    status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
    return status_map.get(status, "Unknown")


def get_status_color(status: int) -> str:
    """Get status color."""
    color_map = {0: "warning", 1: "info", 2: "danger", 3: "success"}
    return color_map.get(status, "secondary")


def get_review_status_label(status: int) -> str:
    """Get review status label."""
    status_map = {1: "Approved", 2: "Revisi", 3: "Rejected"}
    return status_map.get(status, "Unknown")


def get_review_status_color(status: int) -> str:
    """Get review status color."""
    color_map = {1: "success", 2: "warning", 3: "danger"}
    return color_map.get(status, "secondary")