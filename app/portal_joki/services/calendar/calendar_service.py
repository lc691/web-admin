"""
Portal Joki - Calendar Service

Service untuk manajemen calendar dan penugasan joki.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from calendar import monthrange

from app.portal_joki.repositories.calendar.calendar_repo import (
    PortalJokiCalendarRepository,
)
from app.portal_joki.repositories.calendar.holiday_repo import (
    PortalJokiHolidayRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASSES
# ==========================================================
class CalendarMonthResult:

    def __init__(
        self,
        tahun: int,
        bulan: int,
        month_name: str,
        calendar: List[Dict[str, Any]],
        holidays: List[Dict[str, Any]],
        stats: Optional[Dict[str, Any]] = None,
    ):
        self.tahun = tahun
        self.bulan = bulan
        self.month_name = month_name
        self.calendar = calendar
        self.holidays = holidays
        self.stats = stats or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tahun": self.tahun,
            "bulan": self.bulan,
            "month_name": self.month_name,
            "calendar": self.calendar,
            "holidays": self.holidays,
            "stats": self.stats,
        }
    

class CalendarDayResult:
    """
    Result object untuk calendar harian.
    """
    
    def __init__(
        self,
        data: List[Dict[str, Any]],
        tanggal: Optional[date] = None,
        stats: Optional[Dict[str, Any]] = None,
    ):
        self.data = data
        self.tanggal = tanggal or date.today()
        self.stats = stats or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tanggal": self.tanggal.isoformat(),
            "data": self.data,
            "stats": self.stats,
        }
    
    @property
    def total_tasks(self) -> int:
        """Total penugasan hari ini."""
        return len(self.data)
    
    @property
    def total_joki(self) -> int:
        """Total joki yang bertugas."""
        return len(set(item.get("joki_id") for item in self.data if item.get("joki_id")))
    
    @property
    def total_kloter(self) -> int:
        """Total kloter yang bertugas."""
        return len(set(item.get("kloter_id") for item in self.data if item.get("kloter_id")))
    
    @property
    def completion_rate(self) -> float:
        """Completion rate hari ini."""
        total = self.total_tasks
        if total == 0:
            return 0.0
        
        completed = sum(1 for item in self.data if item.get("status") == 3)
        return round((completed / total) * 100, 2)


# ==========================================================
# CALENDAR SERVICE
# ==========================================================
class PortalJokiCalendarService:
    """
    Service Calendar Portal Joki.
    
    Menyediakan fungsi untuk:
    - Calendar bulanan (joki & admin)
    - Calendar harian (joki & admin)
    - Statistik calendar
    - Export calendar
    """

    # ==========================================================
    # UTILITY METHODS
    # ==========================================================

    @staticmethod
    def get_month_names(year: int) -> List[str]:
        """
        Mendapatkan list nama bulan untuk tahun tertentu.
        
        Args:
            year: Tahun
            
        Returns:
            List[str]: List nama bulan (Januari - Desember)
        """
        return [date(year, month, 1).strftime("%B") for month in range(1, 13)]
    
    @staticmethod
    def get_month_name(year: int, month: int) -> str:
        """
        Mendapatkan nama bulan untuk tahun dan bulan tertentu.
        
        Args:
            year: Tahun
            month: Bulan (1-12)
            
        Returns:
            str: Nama bulan
        """
        try:
            return date(year, month, 1).strftime("%B")
        except ValueError:
            return ""

    # ==========================================================
    # JOKI - MONTH
    # ==========================================================

    @staticmethod
    def month(
        *,
        joki_id: int,
        tahun: Optional[int] = None,
        bulan: Optional[int] = None,
    ) -> CalendarMonthResult:
        """
        Mendapatkan calendar bulanan untuk joki.
        """
        today = date.today()

        if tahun is None:
            tahun = today.year
        if bulan is None:
            bulan = today.month

        log.info(
            f"Get calendar month: joki_id={joki_id}, tahun={tahun}, bulan={bulan}"
        )

        # ==========================================================
        # CALENDAR
        # ==========================================================

        calendar = PortalJokiCalendarRepository.get_month(
            joki_id=joki_id,
            tahun=tahun,
            bulan=bulan,
        )

        calendar = PortalJokiCalendarService._enrich_calendar(
            calendar,
        )

        grid = PortalJokiCalendarService._build_calendar_grid(
            tahun=tahun,
            bulan=bulan,
            calendar=calendar,
        )

        # ==========================================================
        # HOLIDAYS
        # ==========================================================

        holidays = PortalJokiHolidayRepository.get_month(
            tahun=tahun,
            bulan=bulan,
        )

        # ==========================================================
        # STATS
        # ==========================================================

        stats = PortalJokiCalendarRepository.get_joki_stats(
            joki_id=joki_id,
            tahun=tahun,
            bulan=bulan,
        )

        stats = PortalJokiCalendarService._build_month_summary(
            calendar=grid,
            stats=stats,
        )

        log.debug(
            f"Calendar month: {len(calendar)} days, {len(holidays)} holidays"
        )

        return CalendarMonthResult(
            tahun=tahun,
            bulan=bulan,
            month_name=PortalJokiCalendarService.get_month_name(
                tahun,
                bulan,
            ),
            calendar=grid,
            holidays=holidays,
            stats=stats,
        )

    # ==========================================================
    # JOKI - DAY
    # ==========================================================

    @staticmethod
    def day(
        *,
        joki_id: int,
        tanggal: Optional[date] = None,
    ) -> CalendarDayResult:
        """
        Mendapatkan calendar harian untuk joki.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal (default: hari ini)
            
        Returns:
            CalendarDayResult: Data calendar harian
        """
        if tanggal is None:
            tanggal = date.today()
        
        log.info(f"Get calendar day: joki_id={joki_id}, tanggal={tanggal}")
        
        data = PortalJokiCalendarRepository.get_day(
            joki_id=joki_id,
            tanggal=tanggal,
        )

        stats = PortalJokiCalendarService._build_day_summary(data)

        log.debug(f"Calendar day: {len(data)} tasks")

        return CalendarDayResult(
            data=data,
            tanggal=tanggal,
            stats=stats,
        )

    # ==========================================================
    # JOKI - WEEK
    # ==========================================================

    @staticmethod
    def week(
        *,
        joki_id: int,
        tanggal: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan calendar mingguan untuk joki.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal referensi (default: hari ini)
            
        Returns:
            dict: Data calendar mingguan
        """
        if tanggal is None:
            tanggal = date.today()
        
        # Get start and end of week
        start_of_week = tanggal - timedelta(days=tanggal.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        log.info(f"Get calendar week: joki_id={joki_id}, week={start_of_week} - {end_of_week}")

        result = []

        current = start_of_week

        while current <= end_of_week:

            day_data = PortalJokiCalendarRepository.get_day(
                joki_id=joki_id,
                tanggal=current,
            )

            summary = PortalJokiCalendarService._build_day_summary(day_data)

            result.append({
                "tanggal": current.isoformat(),
                "hari": current.strftime("%A"),
                "data": day_data,
                **summary,
            })

            current += timedelta(days=1)

        week_summary = PortalJokiCalendarService._build_week_summary(result)

        log.debug(f"Calendar week: {len(result)} days")

        return {
            "start_date": start_of_week.isoformat(),
            "end_date": end_of_week.isoformat(),
            "days": result,
            "summary": week_summary,
        }

    # ==========================================================
    # ADMIN - MONTH
    # ==========================================================

    @staticmethod
    def month_admin(
        *,
        tahun: Optional[int] = None,
        bulan: Optional[int] = None,
    ) -> CalendarMonthResult:
        """
        Mendapatkan calendar bulanan untuk admin.
        
        Args:
            tahun: Tahun (default: tahun ini)
            bulan: Bulan (default: bulan ini)
            
        Returns:
            CalendarMonthResult: Data calendar bulanan admin
        """
        today = date.today()
        
        if tahun is None:
            tahun = today.year
        if bulan is None:
            bulan = today.month
        
        log.info(f"Get admin calendar month: tahun={tahun}, bulan={bulan}")
        
        # Holiday
        holidays = PortalJokiHolidayRepository.get_month(
            tahun=tahun,
            bulan=bulan,
        )

        # Calendar
        calendar = PortalJokiCalendarRepository.get_admin_month(
            tahun=tahun,
            bulan=bulan,
        )

        calendar = PortalJokiCalendarService._enrich_calendar(
            calendar,
        )

        grid = PortalJokiCalendarService._build_calendar_grid(
            tahun=tahun,
            bulan=bulan,
            calendar=calendar,
        )

        # Stats
        stats = PortalJokiCalendarRepository.get_admin_stats(
            tahun=tahun,
            bulan=bulan,
        )

        stats = PortalJokiCalendarService._build_month_summary(
            calendar=grid,
            stats=stats,
        )

        return CalendarMonthResult(
            tahun=tahun,
            bulan=bulan,
            month_name=PortalJokiCalendarService.get_month_name(
                tahun,
                bulan,
            ),
            calendar=grid,
            holidays=holidays,
            stats=stats,
        )

    # ==========================================================
    # ADMIN - DAY
    # ==========================================================

    @staticmethod
    def day_admin(
        *,
        tanggal: Optional[date] = None,
    ) -> CalendarDayResult:
        """
        Mendapatkan calendar harian untuk admin.
        
        Args:
            tanggal: Tanggal (default: hari ini)
            
        Returns:
            CalendarDayResult: Data calendar harian admin
        """
        if tanggal is None:
            tanggal = date.today()
        
        log.info(f"Get admin calendar day: tanggal={tanggal}")
        
        data = PortalJokiCalendarRepository.get_admin_day(
            tanggal=tanggal,
        )

        stats = PortalJokiCalendarService._build_day_summary(data)

        log.debug(f"Calendar day: {len(data)} tasks")

        return CalendarDayResult(
            data=data,
            tanggal=tanggal,
            stats=stats,
        )

    # ==========================================================
    # ADMIN - WEEK
    # ==========================================================

    @staticmethod
    def week_admin(
        *,
        tanggal: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan calendar mingguan untuk admin.
        
        Args:
            tanggal: Tanggal referensi (default: hari ini)
            
        Returns:
            dict: Data calendar mingguan admin
        """
        if tanggal is None:
            tanggal = date.today()
        
        start_of_week = tanggal - timedelta(days=tanggal.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        log.info(f"Get admin calendar week: {start_of_week} - {end_of_week}")
        
        result = []
        current = start_of_week
        
        while current <= end_of_week:
            day_data = PortalJokiCalendarRepository.get_admin_day(
                tanggal=current,
            )

            summary = PortalJokiCalendarService._build_day_summary(day_data)
            
            result.append({
                "tanggal": current.isoformat(),
                "hari": current.strftime("%A"),
                "data": day_data,
                **summary,
            })
            
            current += timedelta(days=1)

        week_summary = PortalJokiCalendarService._build_week_summary(result)
        
        log.debug(f"Admin calendar week: {len(result)} days")
        
        return {
            "start_date": start_of_week.isoformat(),
            "end_date": end_of_week.isoformat(),
            "days": result,
            "summary": week_summary,
        }

    @staticmethod
    def _enrich_calendar(
        calendar: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Mengubah seluruh data calendar menjadi ViewModel.
        """

        return [
            PortalJokiCalendarService._build_view_model(day)
            for day in calendar
        ]

    @staticmethod
    def _build_view_model(
        day: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Membangun ViewModel untuk satu hari calendar.

        Semua informasi yang dibutuhkan template dibentuk di sini.
        """

        item = dict(day)

        PortalJokiCalendarService._build_day(item)
        PortalJokiCalendarService._build_progress(item)
        PortalJokiCalendarService._build_heat(item)
        PortalJokiCalendarService._build_priority(item)
        PortalJokiCalendarService._build_summary(item)
        PortalJokiCalendarService._build_status_badges(item)
        PortalJokiCalendarService._build_tooltip(item)

        return item

    @staticmethod
    def _build_day(
        item: Dict[str, Any],
    ) -> None:

        pending = int(item.get("pending", 0) or 0)
        upload = int(item.get("upload", 0) or 0)
        revisi = int(item.get("revisi", 0) or 0)
        selesai = int(item.get("selesai", 0) or 0)

        total = int(
            item.get(
                "total_tasks",
                item.get("total", 0),
            )
            or 0
        )

        item["pending"] = pending
        item["upload"] = upload
        item["revisi"] = revisi
        item["selesai"] = selesai
        item["total_tasks"] = total

        item["has_task"] = total > 0
        item["is_empty"] = total == 0

        status_count = {
            "pending": pending,
            "upload": upload,
            "revisi": revisi,
            "selesai": selesai,
        }

        dominant = max(status_count, key=status_count.get)

        if status_count[dominant] == 0:
            dominant = "none"

        item["dominant_status"] = dominant

        # ======================================================
        # DATE METADATA
        # ======================================================

        tanggal = item.get("tanggal") or item.get("date")

        if tanggal:
            if isinstance(tanggal, str):
                tanggal = date.fromisoformat(tanggal)

            item["tanggal"] = tanggal.isoformat()
            item["day"] = tanggal.day
            item["month"] = tanggal.month
            item["year"] = tanggal.year
            item["weekday"] = tanggal.weekday()
            item["weekday_name"] = tanggal.strftime("%A")

            item["is_today"] = tanggal == date.today()
            item["is_weekend"] = tanggal.weekday() >= 5

        else:
            item.setdefault("day", 0)
            item.setdefault("month", 0)
            item.setdefault("year", 0)
            item.setdefault("weekday", 0)
            item.setdefault("weekday_name", "")
            item["is_today"] = False
            item["is_weekend"] = False

        item["is_holiday"] = bool(
            item.get("holiday_name")
            or item.get("holiday")
        )

    @staticmethod
    def _build_progress(
        item: Dict[str, Any],
    ) -> None:

        total = item["total_tasks"]
        selesai = item["selesai"]

        if total:
            progress = round((selesai / total) * 100)
        else:
            progress = 0

        item["progress"] = progress

    @staticmethod
    def _build_heat(
        item: Dict[str, Any],
    ) -> None:
        """
        Menentukan tingkat kepadatan pekerjaan (heatmap).
        """

        total = item["total_tasks"]

        if total == 0:
            level = "none"
            css = "heat-none"
            color = "secondary"

        elif total <= 3:
            level = "low"
            css = "heat-low"
            color = "success"

        elif total <= 6:
            level = "medium"
            css = "heat-medium"
            color = "warning"

        elif total <= 10:
            level = "high"
            css = "heat-high"
            color = "danger"

        else:
            level = "very-high"
            css = "heat-critical"
            color = "dark"

        item["heat_level"] = level
        item["heat_class"] = css
        item["heat_color"] = color

    @staticmethod
    def _build_priority(
        item: Dict[str, Any],
    ) -> None:
        """
        Menentukan prioritas berdasarkan jumlah pekerjaan
        dan status dominan.
        """

        total = item["total_tasks"]
        dominant = item["dominant_status"]

        if total == 0:
            priority = "empty"
            icon = "ti ti-calendar-off"

        elif total >= 12:
            priority = "critical"
            icon = "ti ti-alert-octagon"

        elif total >= 8:
            priority = "high"
            icon = "ti ti-alert-circle"

        elif total >= 4:
            priority = "medium"
            icon = "ti ti-clock"

        else:
            priority = "normal"
            icon = "ti ti-check"

        if dominant == "pending":
            color = "warning"

        elif dominant == "upload":
            color = "info"

        elif dominant == "revisi":
            color = "danger"

        elif dominant == "selesai":
            color = "success"

        else:
            color = "secondary"

        item["priority"] = priority
        item["priority_color"] = color
        item["priority_icon"] = icon

    @staticmethod
    def _build_summary(
        item: Dict[str, Any],
    ) -> None:
        """
        Membuat ringkasan status dalam format singkat.
        """

        pending = item["pending"]
        upload = item["upload"]
        revisi = item["revisi"]
        selesai = item["selesai"]

        parts = []

        if pending:
            parts.append(f"P{pending}")

        if upload:
            parts.append(f"U{upload}")

        if revisi:
            parts.append(f"R{revisi}")

        if selesai:
            parts.append(f"S{selesai}")

        item["summary"] = " ".join(parts)

        item["summary_html"] = " ".join([
            f'<span class="text-warning">P{pending}</span>' if pending else "",
            f'<span class="text-info">U{upload}</span>' if upload else "",
            f'<span class="text-danger">R{revisi}</span>' if revisi else "",
            f'<span class="text-success">S{selesai}</span>' if selesai else "",
        ]).strip()

    @staticmethod
    def _build_status_badges(
        item: Dict[str, Any],
    ) -> None:
        """
        Membuat daftar badge status yang siap digunakan oleh template.
        """

        mapping = [
            (
                "pending",
                "Pending",
                "P",
                "warning",
                "ti ti-clock",
            ),
            (
                "upload",
                "Upload",
                "U",
                "info",
                "ti ti-upload",
            ),
            (
                "revisi",
                "Revisi",
                "R",
                "danger",
                "ti ti-refresh",
            ),
            (
                "selesai",
                "Selesai",
                "S",
                "success",
                "ti ti-check",
            ),
        ]

        badges = []

        for key, label, short, color, icon in mapping:

            value = int(item.get(key, 0))

            if value == 0:
                continue

            badges.append(
                {
                    "key": key,
                    "label": label,
                    "short": short,
                    "value": value,
                    "text": f"{short}{value}",
                    "color": color,
                    "icon": icon,
                    "class": f"bg-{color}-lt text-{color}",
                }
            )

        item["status_badges"] = badges

        item["status_count"] = len(badges)

    @staticmethod
    def _build_tooltip(
        item: Dict[str, Any],
    ) -> None:
        """
        Membangun informasi tooltip untuk setiap hari calendar.
        """

        total = item["total_tasks"]

        lines = []

        # Header
        tanggal = item.get("tanggal") or item.get("date") or ""

        if tanggal:
            lines.append(str(tanggal))
            lines.append("")

        # Holiday
        holiday_name = (
            item.get("holiday_name")
            or item.get("holiday")
            or ""
        )

        if holiday_name:
            lines.append(f"🎉 {holiday_name}")
            lines.append("")

        # Summary
        lines.extend(
            [
                f"Total     : {total}",
                f"Pending   : {item['pending']}",
                f"Upload    : {item['upload']}",
                f"Revisi    : {item['revisi']}",
                f"Selesai   : {item['selesai']}",
                "",
                f"Progress  : {item['progress']}%",
            ]
        )

        if item["priority"] != "empty":
            lines.append(f"Priority  : {item['priority'].title()}")

        item["tooltip"] = "\n".join(lines)

        # Versi HTML (untuk Bootstrap/Tippy.js)
        item["tooltip_html"] = (
            "<strong>{}</strong><br>"
            "Total : {}<br>"
            "Pending : {}<br>"
            "Upload : {}<br>"
            "Revisi : {}<br>"
            "Selesai : {}<br>"
            "Progress : {}%"
        ).format(
            tanggal,
            total,
            item["pending"],
            item["upload"],
            item["revisi"],
            item["selesai"],
            item["progress"],
        )

        # Metadata
        item["tooltip_data"] = {
            "date": tanggal,
            "total": total,
            "pending": item["pending"],
            "upload": item["upload"],
            "revisi": item["revisi"],
            "selesai": item["selesai"],
            "progress": item["progress"],
            "priority": item["priority"],
            "heat_level": item["heat_level"],
            "holiday": holiday_name,
        }

    @staticmethod
    def _build_calendar_grid(
        *,
        tahun: int,
        bulan: int,
        calendar: List[Dict[str, Any]],
    ) -> List[List[Optional[Dict[str, Any]]]]:
        """
        Mengubah data calendar menjadi grid 6x7.

        Minggu dimulai hari Senin.

        Returns:
            [
                [day, day, ..., day],   # Week 1
                ...
            ]
        """

        # Index berdasarkan tanggal
        calendar_map = {}

        for day in calendar:

            tanggal = (
                day.get("tanggal")
                or day.get("date")
            )

            if tanggal:
                calendar_map[str(tanggal)] = day

        # Hari pertama (0=Senin)
        first_weekday, total_days = monthrange(tahun, bulan)

        grid: List[List[Optional[Dict[str, Any]]]] = []

        week: List[Optional[Dict[str, Any]]] = []

        # Padding awal
        for _ in range(first_weekday):
            week.append({
                "is_padding": True,
            })

        # Isi tanggal
        for day in range(1, total_days + 1):

            tanggal = date(
                tahun,
                bulan,
                day,
            ).isoformat()

            item = calendar_map.get(
                tanggal,
                    {
                        "tanggal": tanggal,
                        "day": day,

                        "pending": 0,
                        "upload": 0,
                        "revisi": 0,
                        "selesai": 0,

                        "total_tasks": 0,
                        "progress": 0,

                        "summary": "",
                        "summary_html": "",

                        "status_badges": [],
                        "status_count": 0,

                        "has_task": False,
                        "is_empty": True,

                        "dominant_status": "none",

                        "heat_level": "none",
                        "heat_class": "heat-none",
                        "heat_color": "secondary",

                        "priority": "empty",
                        "priority_color": "secondary",
                        "priority_icon": "ti ti-calendar-off",

                        "tooltip": tanggal,
                        "tooltip_html": "",
                        "tooltip_data": {},

                        "is_today": False,
                        "is_weekend": False,
                        "is_holiday": False,
                    },
            )

            item["day"] = day

            week.append(item)

            if len(week) == 7:
                grid.append(week)
                week = []

        # Padding akhir
        while len(week) < 7:
            week.append({
                "is_padding": True,
            })

        if week:
            grid.append(week)

        # Selalu 6 minggu agar tinggi kalender stabil
        while len(grid) < 6:
            grid.append([
                {"is_padding": True}
                for _ in range(7)
            ])

        return grid

    @staticmethod
    def _build_month_summary(
        calendar: List[List[Optional[Dict[str, Any]]]],
        stats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Membangun ringkasan statistik bulanan.

        Args:
            calendar: Calendar grid (6x7) yang telah diperkaya.
            stats: Statistik dari repository (opsional).

        Returns:
            dict
        """

        stats = dict(stats or {})

        # Flatten calendar grid
        calendar_days = [
            day
            for week in calendar
            for day in week
            if day is not None
        ]

        total_days = len(calendar_days)

        total_tasks = 0
        pending = 0
        upload = 0
        revisi = 0
        selesai = 0

        holiday = 0
        busy_day = 0
        active_day = 0
        empty_day = 0

        max_task = 0
        min_task = None

        busiest_day = None

        for day in calendar_days:

            total = day.get("total_tasks", 0)

            total_tasks += total

            pending += day.get("pending", 0)
            upload += day.get("upload", 0)
            revisi += day.get("revisi", 0)
            selesai += day.get("selesai", 0)

            if day.get("is_holiday", False):
                holiday += 1

            if day.get("is_empty", True):
                empty_day += 1
            else:
                active_day += 1

            if day.get("priority") in (
                "high",
                "critical",
            ):
                busy_day += 1

            if total > max_task:
                max_task = total
                busiest_day = {
                    "tanggal": day.get("tanggal"),
                    "day": day.get("day"),
                    "total_tasks": total,
                }

            if min_task is None:
                min_task = total
            else:
                min_task = min(min_task, total)

        completion = (
            round((selesai / total_tasks) * 100, 2)
            if total_tasks
            else 0
        )

        avg_task = (
            round(total_tasks / total_days, 2)
            if total_days
            else 0
        )

        if avg_task <= 3:
            workload = "light"
        elif avg_task <= 6:
            workload = "normal"
        elif avg_task <= 10:
            workload = "busy"
        else:
            workload = "critical"

        if completion >= 80:
            completion_color = "success"
        elif completion >= 50:
            completion_color = "warning"
        else:
            completion_color = "danger"

        stats.update(
            {
                # Calendar
                "total_days": total_days,
                "active_day": active_day,
                "empty_day": empty_day,
                "holiday": holiday,
                "busy_day": busy_day,

                # Task
                "total_tasks": total_tasks,
                "pending": pending,
                "upload": upload,
                "revisi": revisi,
                "selesai": selesai,

                # Completion
                "completion": completion,
                "completion_label": f"{completion:.0f}%",
                "completion_color": completion_color,

                # Statistics
                "avg_task": avg_task,
                "max_task": max_task,
                "min_task": min_task or 0,

                # Workload
                "workload": workload,

                # Peak
                "busiest_day": busiest_day,

                # Flags
                "has_task": total_tasks > 0,
                "is_empty": total_tasks == 0,
            }
        )

        return stats

    @staticmethod
    def _build_day_summary(
        data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Membangun ringkasan statistik harian.

        Digunakan oleh:
        - day()
        - day_admin()
        """

        total = len(data)

        pending = 0
        upload = 0
        revisi = 0
        selesai = 0

        joki_ids = set()
        kloter_ids = set()

        for item in data:

            status = int(item.get("status", -1))

            if status == 0:
                pending += 1

            elif status == 1:
                upload += 1

            elif status == 2:
                revisi += 1

            elif status == 3:
                selesai += 1

            joki_id = item.get("joki_id")
            if joki_id:
                joki_ids.add(joki_id)

            kloter_id = item.get("kloter_id")
            if kloter_id:
                kloter_ids.add(kloter_id)

        progress = (
            round((selesai / total) * 100, 2)
            if total
            else 0
        )

        if total == 0:
            workload = "empty"

        elif total <= 5:
            workload = "light"

        elif total <= 10:
            workload = "normal"

        elif total <= 20:
            workload = "busy"

        else:
            workload = "overload"

        if total == 0:
            dominant_status = "none"
        else:
            status_counts = {
                "pending": pending,
                "upload": upload,
                "revisi": revisi,
                "selesai": selesai,
            }
            dominant_status = max(status_counts, key=status_counts.get)

        return {
            # Task
            "total": total,
            "pending": pending,
            "upload": upload,
            "revisi": revisi,
            "selesai": selesai,

            # Progress
            "progress": progress,
            "completion": progress,
            "completion_label": f"{progress:.0f}%",

            # Resource
            "total_joki": len(joki_ids),
            "total_kloter": len(kloter_ids),

            # Workload
            "workload": workload,
            "dominant_status": dominant_status,

            # Flags
            "has_task": total > 0,
            "is_empty": total == 0,

            # Badges
            "summary": " ".join(filter(None, [
                f"P{pending}" if pending else "",
                f"U{upload}" if upload else "",
                f"R{revisi}" if revisi else "",
                f"S{selesai}" if selesai else "",
            ])),
        }

    @staticmethod
    def _build_week_summary(
        days: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Membangun ringkasan statistik mingguan.

        Args:
            days: List hasil week() yang telah diproses.

        Returns:
            dict: Ringkasan statistik mingguan.
        """

        total_days = len(days)

        total_tasks = 0
        total_completed = 0

        pending = 0
        upload = 0
        revisi = 0
        selesai = 0

        active_days = 0
        empty_days = 0
        busy_days = 0

        max_tasks = 0
        min_tasks = None

        busiest_day = None

        for day in days:

            total = int(day.get("total", 0))

            total_tasks += total

            pending += int(day.get("pending", 0))
            upload += int(day.get("upload", 0))
            revisi += int(day.get("revisi", 0))
            selesai += int(day.get("selesai", 0))

            total_completed += int(day.get("selesai", 0))

            if total > 0:
                active_days += 1
            else:
                empty_days += 1

            if total >= 8:
                busy_days += 1

            if total > max_tasks:
                max_tasks = total
                busiest_day = {
                    "tanggal": day.get("tanggal"),
                    "hari": day.get("hari"),
                    "total": total,
                }

            if min_tasks is None:
                min_tasks = total
            else:
                min_tasks = min(min_tasks, total)

        completion = (
            round((total_completed / total_tasks) * 100, 2)
            if total_tasks
            else 0
        )

        avg_tasks = (
            round(total_tasks / total_days, 2)
            if total_days
            else 0
        )

        if total_tasks == 0:
            workload = "empty"
        elif avg_tasks <= 5:
            workload = "light"
        elif avg_tasks <= 10:
            workload = "normal"
        elif avg_tasks <= 20:
            workload = "busy"
        else:
            workload = "overload"

        return {
            # Summary
            "total_days": total_days,
            "active_days": active_days,
            "empty_days": empty_days,
            "busy_days": busy_days,

            # Task
            "total_tasks": total_tasks,
            "pending": pending,
            "upload": upload,
            "revisi": revisi,
            "selesai": selesai,

            # Progress
            "total_completed": total_completed,
            "completion": completion,
            "completion_label": f"{completion:.0f}%",

            # Average
            "avg_tasks": avg_tasks,
            "max_tasks": max_tasks,
            "min_tasks": min_tasks or 0,

            # Workload
            "workload": workload,

            # Peak
            "busiest_day": busiest_day,

            # Flags
            "has_task": total_tasks > 0,
            "is_empty": total_tasks == 0,
        }

    # ==========================================================
    # HOLIDAYS
    # ==========================================================

    @staticmethod
    def get_holidays(
        *,
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan data holiday.
        
        Args:
            tahun: Tahun
            bulan: Bulan
            
        Returns:
            List[dict]: Data holiday
        """
        log.debug(f"Get holidays: tahun={tahun}, bulan={bulan}")
        return PortalJokiHolidayRepository.get_month(
            tahun=tahun,
            bulan=bulan,
        )

    @staticmethod
    def get_holiday_by_date(
        tanggal: date,
    ) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan holiday berdasarkan tanggal.
        
        Args:
            tanggal: Tanggal
            
        Returns:
            dict: Data holiday atau None
        """
        log.debug(f"Get holiday by date: {tanggal}")
        return PortalJokiHolidayRepository.get_by_date(tanggal)

    @staticmethod
    def is_holiday(
        tanggal: date,
    ) -> bool:
        """
        Cek apakah tanggal adalah hari libur.
        
        Args:
            tanggal: Tanggal yang dicek
            
        Returns:
            bool: True jika hari libur
        """
        return PortalJokiHolidayRepository.is_holiday(tanggal)

    # ==========================================================
    # STATISTICS
    # ==========================================================

    @staticmethod
    def get_stats(
        *,
        joki_id: Optional[int] = None,
        tahun: Optional[int] = None,
        bulan: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan statistik calendar.
        
        Args:
            joki_id: ID joki (opsional, untuk joki spesifik)
            tahun: Tahun (default: tahun ini)
            bulan: Bulan (default: bulan ini)
            
        Returns:
            dict: Statistik calendar
        """
        today = date.today()
        
        if tahun is None:
            tahun = today.year
        if bulan is None:
            bulan = today.month
        
        if joki_id:
            stats = PortalJokiCalendarRepository.get_joki_stats(
                joki_id=joki_id,
                tahun=tahun,
                bulan=bulan,
            )
            log.debug(f"Get stats for joki: {joki_id}")
        else:
            stats = PortalJokiCalendarRepository.get_admin_stats(
                tahun=tahun,
                bulan=bulan,
            )
            log.debug(f"Get admin stats: tahun={tahun}, bulan={bulan}")
        
        return stats or {}

    # ==========================================================
    # EXPORT
    # ==========================================================

    @staticmethod
    def export_month(
        *,
        joki_id: Optional[int] = None,
        tahun: int,
        bulan: int,
    ) -> Dict[str, Any]:
        """
        Export data calendar bulanan.
        
        Args:
            joki_id: ID joki (opsional)
            tahun: Tahun
            bulan: Bulan
            
        Returns:
            dict: Data export
        """
        log.info(f"Export month: joki_id={joki_id}, tahun={tahun}, bulan={bulan}")
        
        if joki_id:
            result = PortalJokiCalendarService.month(
                joki_id=joki_id,
                tahun=tahun,
                bulan=bulan,
            )
        else:
            result = PortalJokiCalendarService.month_admin(
                tahun=tahun,
                bulan=bulan,
            )
        
        return {
            "metadata": {
                "tahun": tahun,
                "bulan": bulan,
                "exported_at": datetime.now().isoformat(),
                "joki_id": joki_id,
            },
            "summary": result.stats,
            "calendar": result.calendar,
            "holidays": result.holidays,
            "stats": result.stats,
        }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
calendar_service = PortalJokiCalendarService()