"""
Portal Joki - Statistik Service

Service untuk statistik portal joki.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta

from app.portal_joki.repositories.laporan.laporan_repo import (
    PortalJokiLaporanRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class StatistikResult:
    """
    Result object untuk statistik.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        period: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.period = period or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "period": self.period,
        }
    
    @classmethod
    def ok(
        cls,
        data: Dict[str, Any],
        period: Optional[Dict[str, Any]] = None,
    ) -> "StatistikResult":
        """Create success result."""
        return cls(True, "OK", data, period or {})
    
    @classmethod
    def error(cls, message: str) -> "StatistikResult":
        """Create error result."""
        return cls(False, message, {}, {})
    
    @property
    def total(self) -> int:
        """Total penugasan."""
        return self.data.get("total", 0)
    
    @property
    def pending(self) -> int:
        """Total pending."""
        return self.data.get("pending", 0)
    
    @property
    def upload(self) -> int:
        """Total upload."""
        return self.data.get("upload", 0)
    
    @property
    def revisi(self) -> int:
        """Total revisi."""
        return self.data.get("revisi", 0)
    
    @property
    def selesai(self) -> int:
        """Total selesai."""
        return self.data.get("selesai", 0)
    
    @property
    def total_target(self) -> int:
        """Total target judul."""
        return self.data.get("total_target", 0)
    
    @property
    def completion_rate(self) -> float:
        """Completion rate."""
        total = self.total
        if total == 0:
            return 0.0
        return round((self.selesai / total) * 100, 2)
    
    @property
    def pending_rate(self) -> float:
        """Pending rate."""
        total = self.total
        if total == 0:
            return 0.0
        return round((self.pending / total) * 100, 2)


# ==========================================================
# STATISTIK SERVICE
# ==========================================================
class PortalJokiStatistikService:
    """
    Service Statistik Portal Joki.
    
    Menyediakan fungsi untuk:
    - Statistik keseluruhan
    - Statistik per periode
    - Statistik per joki
    - Statistik per kloter
    - Statistik trend
    - Statistik perbandingan
    """

    @staticmethod
    def execute(
        period: Optional[str] = None,
    ) -> StatistikResult:
        """
        Mendapatkan statistik keseluruhan.
        
        Args:
            period: Periode (opsional: "all", "month", "week", "today")
            
        Returns:
            StatistikResult: Statistik
        """
        log.info(f"Get statistik: period={period}")
        
        try:
            # If period specified, get period stats
            if period:
                today = date.today()
                
                if period == "today":
                    start_date = today
                    end_date = today
                elif period == "week":
                    start_date = today - timedelta(days=today.weekday())
                    end_date = start_date + timedelta(days=6)
                elif period == "month":
                    start_date = date(today.year, today.month, 1)
                    end_date = date(today.year, today.month, 28)  # Will be adjusted
                else:
                    start_date = None
                    end_date = None
                
                if start_date and end_date:
                    data = PortalJokiLaporanRepository.get_statistik_period(
                        start_date, end_date
                    )
                    period_info = {
                        "type": period,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                    }
                    return StatistikResult.ok(data or {}, period_info)
            
            # Default: all time
            data = PortalJokiLaporanRepository.get_statistik()
            
            period_info = {
                "type": "all",
                "start_date": None,
                "end_date": None,
            }
            
            log.debug(f"Statistik: total={data.get('total', 0)}, selesai={data.get('selesai', 0)}")
            
            return StatistikResult.ok(data or {}, period_info)
            
        except Exception as e:
            log.error(f"Failed to get statistik: {e}")
            return StatistikResult.error(f"Gagal mengambil statistik: {str(e)}")

    @staticmethod
    def execute_by_joki(
        joki_id: int,
        period: Optional[str] = None,
    ) -> StatistikResult:
        """
        Mendapatkan statistik untuk joki tertentu.
        
        Args:
            joki_id: ID joki
            period: Periode (opsional: "all", "month", "week", "today")
            
        Returns:
            StatistikResult: Statistik joki
        """
        log.info(f"Get statistik by joki: joki_id={joki_id}, period={period}")
        
        try:
            # Get period filter
            start_date = None
            end_date = None
            
            if period:
                today = date.today()
                
                if period == "today":
                    start_date = today
                    end_date = today
                elif period == "week":
                    start_date = today - timedelta(days=today.weekday())
                    end_date = start_date + timedelta(days=6)
                elif period == "month":
                    start_date = date(today.year, today.month, 1)
                    end_date = date(today.year, today.month, 28)
            
            # Get stats from repository
            # Note: Currently repository doesn't have get_statistik_by_joki with period
            # We'll use the existing method
            data = PortalJokiLaporanRepository.get_statistik_by_joki(joki_id)
            
            # If period is specified, we could filter in service layer
            # For now, just return what we have
            
            period_info = {
                "type": period or "all",
                "joki_id": joki_id,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            }
            
            log.debug(f"Statistik by joki: total={data.get('total', 0)}, selesai={data.get('selesai', 0)}")
            
            return StatistikResult.ok(data or {}, period_info)
            
        except Exception as e:
            log.error(f"Failed to get statistik by joki: {e}")
            return StatistikResult.error(f"Gagal mengambil statistik joki: {str(e)}")

    @staticmethod
    def execute_by_period(
        start_date: date,
        end_date: date,
    ) -> StatistikResult:
        """
        Mendapatkan statistik dalam periode tertentu.
        
        Args:
            start_date: Tanggal awal
            end_date: Tanggal akhir
            
        Returns:
            StatistikResult: Statistik periode
        """
        log.info(f"Get statistik by period: {start_date} - {end_date}")
        
        try:
            data = PortalJokiLaporanRepository.get_statistik_period(
                start_date, end_date
            )
            
            period_info = {
                "type": "custom",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days + 1,
            }
            
            log.debug(f"Statistik by period: total={data.get('total', 0)}")
            
            return StatistikResult.ok(data or {}, period_info)
            
        except Exception as e:
            log.error(f"Failed to get statistik by period: {e}")
            return StatistikResult.error(f"Gagal mengambil statistik periode: {str(e)}")

    @staticmethod
    def get_trend(
        joki_id: Optional[int] = None,
        months: int = 6,
    ) -> Dict[str, Any]:
        """
        Mendapatkan trend statistik per bulan.
        
        Args:
            joki_id: ID joki (opsional)
            months: Jumlah bulan ke belakang
            
        Returns:
            dict: Trend statistik
        """
        log.info(f"Get statistik trend: joki_id={joki_id}, months={months}")
        
        try:
            data = []
            today = date.today()
            
            for i in range(months):
                month = today.month - i
                year = today.year
                
                if month <= 0:
                    month += 12
                    year -= 1
                
                # Get month data
                month_data = PortalJokiLaporanRepository.get_rekap_bulanan(year, month)
                
                if joki_id:
                    # Get joki specific data
                    joki_stats = PortalJokiLaporanRepository.get_statistik_by_joki(joki_id)
                    # Note: We can't filter by month easily with current repo
                    # This is a simplified version
                
                data.append({
                    "bulan": f"{year}-{month:02d}",
                    "tahun": year,
                    "bulan_num": month,
                    "total": month_data.get("total", 0),
                    "selesai": month_data.get("selesai", 0),
                    "pending": month_data.get("pending", 0),
                    "revisi": month_data.get("revisi", 0),
                    "completion_rate": month_data.get("completion_rate", 0),
                })
            
            return {
                "success": True,
                "data": data,
                "months": months,
                "joki_id": joki_id,
            }
            
        except Exception as e:
            log.error(f"Failed to get statistik trend: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil trend: {str(e)}",
                "data": [],
            }

    @staticmethod
    def get_quick_stats() -> Dict[str, Any]:
        """
        Mendapatkan quick stats untuk dashboard.
        
        Returns:
            dict: Quick stats
        """
        log.debug("Get quick stats")
        
        try:
            # Today stats
            today = date.today()
            today_stats = PortalJokiLaporanRepository.get_statistik_period(today, today)
            
            # Month stats
            month_start = date(today.year, today.month, 1)
            month_end = date(today.year, today.month, 28)
            month_stats = PortalJokiLaporanRepository.get_statistik_period(
                month_start, month_end
            )
            
            # All time stats
            all_stats = PortalJokiLaporanRepository.get_statistik()
            
            return {
                "success": True,
                "today": {
                    "total": today_stats.get("total", 0),
                    "selesai": today_stats.get("selesai", 0),
                    "completion_rate": round(
                        (today_stats.get("selesai", 0) / max(today_stats.get("total", 1), 1)) * 100,
                        2
                    ),
                },
                "month": {
                    "total": month_stats.get("total", 0),
                    "selesai": month_stats.get("selesai", 0),
                    "completion_rate": month_stats.get("completion_rate", 0),
                },
                "all_time": {
                    "total": all_stats.get("total", 0),
                    "selesai": all_stats.get("selesai", 0),
                    "completion_rate": all_stats.get("completion_rate", 0),
                },
            }
            
        except Exception as e:
            log.error(f"Failed to get quick stats: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil quick stats: {str(e)}",
            }

    @staticmethod
    def get_summary() -> Dict[str, Any]:
        """
        Mendapatkan ringkasan statistik lengkap.
        
        Returns:
            dict: Ringkasan statistik
        """
        log.info("Get statistik summary")
        
        try:
            all_stats = PortalJokiLaporanRepository.get_statistik()
            
            # Calculate additional metrics
            total = all_stats.get("total", 0)
            selesai = all_stats.get("selesai", 0)
            pending = all_stats.get("pending", 0)
            revisi = all_stats.get("revisi", 0)
            upload = all_stats.get("upload", 0)
            total_target = all_stats.get("total_target", 0)
            
            return {
                "success": True,
                "summary": {
                    "total_tasks": total,
                    "completed": selesai,
                    "pending": pending,
                    "revision": revisi,
                    "uploaded": upload,
                    "total_target": total_target,
                    "completion_rate": round((selesai / max(total, 1)) * 100, 2),
                    "pending_rate": round((pending / max(total, 1)) * 100, 2),
                    "revision_rate": round((revisi / max(total, 1)) * 100, 2),
                    "upload_rate": round((upload / max(total, 1)) * 100, 2),
                },
                "distribution": {
                    "pending": pending,
                    "upload": upload,
                    "revisi": revisi,
                    "selesai": selesai,
                },
                "target": {
                    "total": total_target,
                    "average_per_task": round(total_target / max(total, 1), 2),
                }
            }
            
        except Exception as e:
            log.error(f"Failed to get statistik summary: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil ringkasan statistik: {str(e)}",
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
statistik_service = PortalJokiStatistikService()