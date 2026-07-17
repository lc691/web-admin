"""
Portal Joki - Calendar Service

Service untuk manajemen calendar dan penugasan joki.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta

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
    """
    Result object untuk calendar bulanan.
    """
    
    def __init__(
        self,
        tahun: int,
        bulan: int,
        calendar: List[Dict[str, Any]],
        holidays: List[Dict[str, Any]],
        stats: Optional[Dict[str, Any]] = None,
    ):
        self.tahun = tahun
        self.bulan = bulan
        self.calendar = calendar
        self.holidays = holidays
        self.stats = stats or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tahun": self.tahun,
            "bulan": self.bulan,
            "calendar": self.calendar,
            "holidays": self.holidays,
            "stats": self.stats,
        }
    
    @property
    def total_days(self) -> int:
        """Total hari dalam bulan."""
        return len(self.calendar)
    
    @property
    def total_holidays(self) -> int:
        """Total hari libur."""
        return len(self.holidays)
    
    @property
    def total_tasks(self) -> int:
        """Total penugasan."""
        return sum(day.get("total", 0) for day in self.calendar)
    
    @property
    def completion_rate(self) -> float:
        """Completion rate bulan ini."""
        total = self.total_tasks
        if total == 0:
            return 0.0
        
        completed = sum(day.get("selesai", 0) for day in self.calendar)
        return round((completed / total) * 100, 2)


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
        
        Args:
            joki_id: ID joki
            tahun: Tahun (default: tahun ini)
            bulan: Bulan (default: bulan ini)
            
        Returns:
            CalendarMonthResult: Data calendar bulanan
        """
        today = date.today()
        
        if tahun is None:
            tahun = today.year
        if bulan is None:
            bulan = today.month
        
        log.info(f"Get calendar month: joki_id={joki_id}, tahun={tahun}, bulan={bulan}")
        
        # Get calendar data
        calendar = PortalJokiCalendarRepository.get_month(
            joki_id=joki_id,
            tahun=tahun,
            bulan=bulan,
        )
        
        # Get holidays
        holidays = PortalJokiHolidayRepository.get_month(
            tahun=tahun,
            bulan=bulan,
        )
        
        # Get stats
        stats = PortalJokiCalendarRepository.get_joki_stats(
            joki_id=joki_id,
            tahun=tahun,
            bulan=bulan,
        )
        
        log.debug(f"Calendar month: {len(calendar)} days, {len(holidays)} holidays")
        
        return CalendarMonthResult(
            tahun=tahun,
            bulan=bulan,
            calendar=calendar,
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
        
        # Calculate stats
        stats = {
            "total": len(data),
            "pending": sum(1 for item in data if item.get("status") == 0),
            "upload": sum(1 for item in data if item.get("status") == 1),
            "revisi": sum(1 for item in data if item.get("status") == 2),
            "selesai": sum(1 for item in data if item.get("status") == 3),
        }
        
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
            
            result.append({
                "tanggal": current.isoformat(),
                "hari": current.strftime("%A"),
                "data": day_data,
                "total": len(day_data),
                "selesai": sum(1 for item in day_data if item.get("status") == 3),
            })
            
            current += timedelta(days=1)
        
        log.debug(f"Calendar week: {len(result)} days")
        
        return {
            "start_date": start_of_week.isoformat(),
            "end_date": end_of_week.isoformat(),
            "days": result,
            "total_tasks": sum(day["total"] for day in result),
            "total_completed": sum(day["selesai"] for day in result),
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
        
        calendar = PortalJokiCalendarRepository.get_admin_month(
            tahun=tahun,
            bulan=bulan,
        )
        
        holidays = PortalJokiHolidayRepository.get_month(
            tahun=tahun,
            bulan=bulan,
        )
        
        stats = PortalJokiCalendarRepository.get_admin_stats(
            tahun=tahun,
            bulan=bulan,
        )
        
        log.debug(f"Admin calendar month: {len(calendar)} days, {len(holidays)} holidays")
        
        return CalendarMonthResult(
            tahun=tahun,
            bulan=bulan,
            calendar=calendar,
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
        
        stats = {
            "total": len(data),
            "total_joki": len(set(item.get("joki_id") for item in data if item.get("joki_id"))),
            "total_kloter": len(set(item.get("kloter_id") for item in data if item.get("kloter_id"))),
            "pending": sum(1 for item in data if item.get("status") == 0),
            "upload": sum(1 for item in data if item.get("status") == 1),
            "revisi": sum(1 for item in data if item.get("status") == 2),
            "selesai": sum(1 for item in data if item.get("status") == 3),
        }
        
        log.debug(f"Admin calendar day: {len(data)} tasks")
        
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
            
            result.append({
                "tanggal": current.isoformat(),
                "hari": current.strftime("%A"),
                "data": day_data,
                "total": len(day_data),
                "selesai": sum(1 for item in day_data if item.get("status") == 3),
            })
            
            current += timedelta(days=1)
        
        log.debug(f"Admin calendar week: {len(result)} days")
        
        return {
            "start_date": start_of_week.isoformat(),
            "end_date": end_of_week.isoformat(),
            "days": result,
            "total_tasks": sum(day["total"] for day in result),
            "total_completed": sum(day["selesai"] for day in result),
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
            "summary": {
                "total_days": result.total_days,
                "total_tasks": result.total_tasks,
                "total_holidays": result.total_holidays,
                "completion_rate": result.completion_rate,
            },
            "calendar": result.calendar,
            "holidays": result.holidays,
            "stats": result.stats,
        }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
calendar_service = PortalJokiCalendarService()