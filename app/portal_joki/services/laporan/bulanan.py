"""
Portal Joki - Laporan Bulanan Service

Service untuk laporan bulanan portal joki.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from calendar import monthrange

from app.portal_joki.repositories.laporan.laporan_repo import (
    PortalJokiLaporanRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class BulananResult:
    """
    Result object untuk laporan bulanan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[List[Dict[str, Any]]] = None,
        stats: Optional[Dict[str, Any]] = None,
        tahun: Optional[int] = None,
        bulan: Optional[int] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or []
        self.stats = stats or {}
        self.tahun = tahun or date.today().year
        self.bulan = bulan or date.today().month
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "tahun": self.tahun,
            "bulan": self.bulan,
            "data": self.data,
            "stats": self.stats,
        }
    
    @classmethod
    def ok(
        cls,
        data: List[Dict[str, Any]],
        tahun: int,
        bulan: int,
        stats: Optional[Dict[str, Any]] = None,
    ) -> "BulananResult":
        """Create success result."""
        return cls(True, "OK", data, stats or {}, tahun, bulan)
    
    @classmethod
    def error(cls, message: str) -> "BulananResult":
        """Create error result."""
        return cls(False, message, [], {}, None, None)
    
    @property
    def total_joki(self) -> int:
        """Total joki."""
        return len(self.data)
    
    @property
    def total_penugasan(self) -> int:
        """Total penugasan."""
        return sum(item.get("total_penugasan", 0) for item in self.data)
    
    @property
    def total_target(self) -> int:
        """Total target judul."""
        return sum(item.get("total_target", 0) for item in self.data)
    
    @property
    def pending(self) -> int:
        """Total pending."""
        return sum(item.get("pending", 0) for item in self.data)
    
    @property
    def upload(self) -> int:
        """Total upload."""
        return sum(item.get("upload", 0) for item in self.data)
    
    @property
    def revisi(self) -> int:
        """Total revisi."""
        return sum(item.get("revisi", 0) for item in self.data)
    
    @property
    def selesai(self) -> int:
        """Total selesai."""
        return sum(item.get("selesai", 0) for item in self.data)
    
    @property
    def completion_rate(self) -> float:
        """Completion rate."""
        total = self.total_penugasan
        if total == 0:
            return 0.0
        return round((self.selesai / total) * 100, 2)
    
    @property
    def average_per_joki(self) -> float:
        """Rata-rata penugasan per joki."""
        total = self.total_joki
        if total == 0:
            return 0.0
        return round(self.total_penugasan / total, 2)


# ==========================================================
# BULANAN SERVICE
# ==========================================================
class PortalJokiBulananService:
    """
    Service Laporan Bulanan Portal Joki.
    
    Menyediakan fungsi untuk:
    - Laporan bulanan semua joki
    - Laporan bulanan detail
    - Rekap bulanan
    - Statistik bulanan
    - Perbandingan bulan
    """

    @staticmethod
    def execute(
        tahun: Optional[int] = None,
        bulan: Optional[int] = None,
    ) -> BulananResult:
        """
        Mendapatkan laporan bulanan per joki.
        
        Args:
            tahun: Tahun (default: tahun ini)
            bulan: Bulan (default: bulan ini)
            
        Returns:
            BulananResult: Laporan bulanan
        """
        today = date.today()
        
        if tahun is None:
            tahun = today.year
        if bulan is None:
            bulan = today.month
        
        # Validasi bulan
        if bulan < 1 or bulan > 12:
            log.warning(f"Invalid month: {bulan}")
            return BulananResult.error("Bulan tidak valid. (1-12)")
        
        log.info(f"Get laporan bulanan: tahun={tahun}, bulan={bulan}")
        
        try:
            data = PortalJokiLaporanRepository.get_bulanan(tahun, bulan)
            
            # Calculate stats
            stats = {
                "total_joki": len(data),
                "total_penugasan": sum(item.get("total_penugasan", 0) for item in data),
                "total_target": sum(item.get("total_target", 0) for item in data),
                "pending": sum(item.get("pending", 0) for item in data),
                "upload": sum(item.get("upload", 0) for item in data),
                "revisi": sum(item.get("revisi", 0) for item in data),
                "selesai": sum(item.get("selesai", 0) for item in data),
                "active_joki": len([item for item in data if item.get("total_penugasan", 0) > 0]),
                "bulan": bulan,
                "tahun": tahun,
                "days_in_month": monthrange(tahun, bulan)[1],
            }
            
            # Hitung completion rate
            total = stats["total_penugasan"]
            if total > 0:
                stats["completion_rate"] = round((stats["selesai"] / total) * 100, 2)
            else:
                stats["completion_rate"] = 0.0
            
            log.debug(f"Laporan bulanan: {len(data)} joki, {stats['total_penugasan']} tasks")
            
            return BulananResult.ok(data, tahun, bulan, stats)
            
        except Exception as e:
            log.error(f"Failed to get laporan bulanan: {e}")
            return BulananResult.error(f"Gagal mengambil laporan bulanan: {str(e)}")

    @staticmethod
    def execute_detail(
        tahun: Optional[int] = None,
        bulan: Optional[int] = None,
        joki_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan laporan bulanan detail per hari.
        
        Args:
            tahun: Tahun (default: tahun ini)
            bulan: Bulan (default: bulan ini)
            joki_id: Filter by joki (opsional)
            
        Returns:
            dict: Laporan bulanan detail
        """
        today = date.today()
        
        if tahun is None:
            tahun = today.year
        if bulan is None:
            bulan = today.month
        
        log.info(f"Get laporan bulanan detail: tahun={tahun}, bulan={bulan}, joki_id={joki_id}")
        
        try:
            data = PortalJokiLaporanRepository.get_bulanan_detail(
                tahun, bulan, joki_id
            )
            
            # Group by tanggal
            days = {}
            for item in data:
                tanggal = item.get("tanggal")
                if tanggal:
                    key = tanggal.isoformat() if hasattr(tanggal, 'isoformat') else str(tanggal)
                    if key not in days:
                        days[key] = []
                    days[key].append(item)
            
            result = {
                "tahun": tahun,
                "bulan": bulan,
                "joki_id": joki_id,
                "total": len(data),
                "days": days,
                "day_count": len(days),
                "completed": sum(1 for item in data if item.get("status") == 3),
                "pending": sum(1 for item in data if item.get("status") == 0),
            }
            
            log.debug(f"Laporan bulanan detail: {len(data)} tasks, {len(days)} days")
            
            return result
            
        except Exception as e:
            log.error(f"Failed to get laporan bulanan detail: {e}")
            return {}

    @staticmethod
    def get_rekap(
        tahun: Optional[int] = None,
        bulan: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan rekap bulanan.
        
        Args:
            tahun: Tahun (default: tahun ini)
            bulan: Bulan (default: bulan ini)
            
        Returns:
            dict: Rekap bulanan
        """
        today = date.today()
        
        if tahun is None:
            tahun = today.year
        if bulan is None:
            bulan = today.month
        
        log.info(f"Get rekap bulanan: tahun={tahun}, bulan={bulan}")
        
        try:
            rekap = PortalJokiLaporanRepository.get_rekap_bulanan(tahun, bulan)
            log.debug(f"Rekap bulanan: {rekap}")
            return rekap or {}
            
        except Exception as e:
            log.error(f"Failed to get rekap bulanan: {e}")
            return {}

    @staticmethod
    def get_comparison(
        tahun1: int,
        bulan1: int,
        tahun2: int,
        bulan2: int,
    ) -> Dict[str, Any]:
        """
        Membandingkan dua bulan.
        
        Args:
            tahun1: Tahun pertama
            bulan1: Bulan pertama
            tahun2: Tahun kedua
            bulan2: Bulan kedua
            
        Returns:
            dict: Perbandingan dua bulan
        """
        log.info(f"Get comparison: {tahun1}-{bulan1} vs {tahun2}-{bulan2}")
        
        try:
            result1 = PortalJokiBulananService.execute(tahun1, bulan1)
            result2 = PortalJokiBulananService.execute(tahun2, bulan2)
            
            if not result1.success or not result2.success:
                return {
                    "success": False,
                    "message": "Gagal mengambil data untuk perbandingan.",
                }
            
            comparison = {
                "success": True,
                "period1": {
                    "tahun": tahun1,
                    "bulan": bulan1,
                    "total_joki": result1.total_joki,
                    "total_penugasan": result1.total_penugasan,
                    "selesai": result1.selesai,
                    "completion_rate": result1.completion_rate,
                    "data": result1.data,
                },
                "period2": {
                    "tahun": tahun2,
                    "bulan": bulan2,
                    "total_joki": result2.total_joki,
                    "total_penugasan": result2.total_penugasan,
                    "selesai": result2.selesai,
                    "completion_rate": result2.completion_rate,
                    "data": result2.data,
                },
                "diff": {
                    "total_penugasan": result2.total_penugasan - result1.total_penugasan,
                    "selesai": result2.selesai - result1.selesai,
                    "completion_rate": round(result2.completion_rate - result1.completion_rate, 2),
                    "total_joki": result2.total_joki - result1.total_joki,
                }
            }
            
            log.debug(f"Comparison complete")
            return comparison
            
        except Exception as e:
            log.error(f"Failed to get comparison: {e}")
            return {
                "success": False,
                "message": f"Gagal membandingkan: {str(e)}",
            }

    @staticmethod
    def get_trend(
        joki_id: Optional[int] = None,
        months: int = 6,
    ) -> Dict[str, Any]:
        """
        Mendapatkan trend performa.
        
        Args:
            joki_id: ID joki (opsional, untuk admin jika None)
            months: Jumlah bulan ke belakang
            
        Returns:
            dict: Trend performa
        """
        log.info(f"Get trend: joki_id={joki_id}, months={months}")
        
        try:
            if joki_id:
                data = PortalJokiLaporanRepository.get_performance_trend(
                    joki_id, months
                )
            else:
                # Admin view - get data from bulanan
                data = []
                today = date.today()
                
                for i in range(months):
                    month = today.month - i
                    year = today.year
                    
                    if month <= 0:
                        month += 12
                        year -= 1
                    
                    result = PortalJokiBulananService.execute(year, month)
                    if result.success:
                        data.append({
                            "bulan": f"{year}-{month:02d}",
                            "total": result.total_penugasan,
                            "selesai": result.selesai,
                            "completion_rate": result.completion_rate,
                            "total_joki": result.total_joki,
                        })
            
            return {
                "success": True,
                "data": data,
                "months": months,
                "joki_id": joki_id,
            }
            
        except Exception as e:
            log.error(f"Failed to get trend: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil trend: {str(e)}",
                "data": [],
            }

    @staticmethod
    def get_yearly_summary(year: Optional[int] = None) -> Dict[str, Any]:
        """
        Mendapatkan ringkasan tahunan.
        
        Args:
            year: Tahun (default: tahun ini)
            
        Returns:
            dict: Ringkasan tahunan
        """
        if year is None:
            year = date.today().year
        
        log.info(f"Get yearly summary: year={year}")
        
        try:
            monthly_data = []
            total_tasks = 0
            total_completed = 0
            
            for month in range(1, 13):
                result = PortalJokiBulananService.execute(year, month)
                if result.success:
                    monthly_data.append({
                        "bulan": month,
                        "total_penugasan": result.total_penugasan,
                        "selesai": result.selesai,
                        "completion_rate": result.completion_rate,
                        "total_joki": result.total_joki,
                    })
                    total_tasks += result.total_penugasan
                    total_completed += result.selesai
            
            return {
                "success": True,
                "year": year,
                "months": monthly_data,
                "total_tasks": total_tasks,
                "total_completed": total_completed,
                "completion_rate": round((total_completed / total_tasks) * 100, 2) if total_tasks > 0 else 0,
                "active_months": len([m for m in monthly_data if m["total_penugasan"] > 0]),
            }
            
        except Exception as e:
            log.error(f"Failed to get yearly summary: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil ringkasan tahunan: {str(e)}",
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
bulanan_service = PortalJokiBulananService()