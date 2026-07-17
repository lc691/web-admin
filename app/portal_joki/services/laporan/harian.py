"""
Portal Joki - Laporan Harian Service

Service untuk laporan harian portal joki.
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
class HarianResult:
    """
    Result object untuk laporan harian.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[List[Dict[str, Any]]] = None,
        stats: Optional[Dict[str, Any]] = None,
        tanggal: Optional[date] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or []
        self.stats = stats or {}
        self.tanggal = tanggal or date.today()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "tanggal": self.tanggal.isoformat(),
            "data": self.data,
            "stats": self.stats,
        }
    
    @classmethod
    def ok(
        cls,
        data: List[Dict[str, Any]],
        tanggal: Optional[date] = None,
        stats: Optional[Dict[str, Any]] = None,
    ) -> "HarianResult":
        """Create success result."""
        return cls(True, "OK", data, stats or {}, tanggal)
    
    @classmethod
    def error(cls, message: str) -> "HarianResult":
        """Create error result."""
        return cls(False, message, [], {}, None)
    
    @property
    def total_tasks(self) -> int:
        """Total penugasan."""
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
    def pending(self) -> int:
        """Total pending."""
        return sum(1 for item in self.data if item.get("status") == 0)
    
    @property
    def upload(self) -> int:
        """Total upload."""
        return sum(1 for item in self.data if item.get("status") == 1)
    
    @property
    def revisi(self) -> int:
        """Total revisi."""
        return sum(1 for item in self.data if item.get("status") == 2)
    
    @property
    def selesai(self) -> int:
        """Total selesai."""
        return sum(1 for item in self.data if item.get("status") == 3)
    
    @property
    def completion_rate(self) -> float:
        """Completion rate."""
        total = self.total_tasks
        if total == 0:
            return 0.0
        return round((self.selesai / total) * 100, 2)
    
    @property
    def total_target(self) -> int:
        """Total target judul."""
        return sum(item.get("target_judul", 0) for item in self.data)


# ==========================================================
# HARIAN SERVICE
# ==========================================================
class PortalJokiHarianService:
    """
    Service Laporan Harian Portal Joki.
    
    Menyediakan fungsi untuk:
    - Laporan harian semua joki
    - Laporan harian per joki
    - Laporan harian per kloter
    - Rekap harian
    - Statistik harian
    """

    @staticmethod
    def execute(
        tanggal: Optional[date] = None,
    ) -> HarianResult:
        """
        Mendapatkan laporan harian untuk semua joki.
        
        Args:
            tanggal: Tanggal laporan (default: hari ini)
            
        Returns:
            HarianResult: Laporan harian
        """
        if tanggal is None:
            tanggal = date.today()
        
        log.info(f"Get laporan harian: tanggal={tanggal}")
        
        try:
            data = PortalJokiLaporanRepository.get_harian(tanggal)
            
            # Calculate stats
            stats = {
                "total": len(data),
                "total_joki": len(set(item.get("joki_id") for item in data if item.get("joki_id"))),
                "total_kloter": len(set(item.get("kloter_id") for item in data if item.get("kloter_id"))),
                "pending": sum(1 for item in data if item.get("status") == 0),
                "upload": sum(1 for item in data if item.get("status") == 1),
                "revisi": sum(1 for item in data if item.get("status") == 2),
                "selesai": sum(1 for item in data if item.get("status") == 3),
                "total_target": sum(item.get("target_judul", 0) for item in data),
            }
            
            log.debug(f"Laporan harian: {len(data)} tasks, {stats['total_joki']} joki")
            
            return HarianResult.ok(data, tanggal, stats)
            
        except Exception as e:
            log.error(f"Failed to get laporan harian: {e}")
            return HarianResult.error(f"Gagal mengambil laporan harian: {str(e)}")

    @staticmethod
    def execute_by_joki(
        tanggal: Optional[date] = None,
        joki_id: Optional[int] = None,
    ) -> HarianResult:
        """
        Mendapatkan laporan harian untuk joki tertentu.
        
        Args:
            tanggal: Tanggal laporan (default: hari ini)
            joki_id: ID joki (wajib)
            
        Returns:
            HarianResult: Laporan harian joki
        """
        if joki_id is None:
            return HarianResult.error("Joki ID wajib diisi.")
        
        if tanggal is None:
            tanggal = date.today()
        
        log.info(f"Get laporan harian by joki: tanggal={tanggal}, joki_id={joki_id}")
        
        try:
            data = PortalJokiLaporanRepository.get_harian_by_joki(tanggal, joki_id)
            
            stats = {
                "total": len(data),
                "joki_id": joki_id,
                "pending": sum(1 for item in data if item.get("status") == 0),
                "upload": sum(1 for item in data if item.get("status") == 1),
                "revisi": sum(1 for item in data if item.get("status") == 2),
                "selesai": sum(1 for item in data if item.get("status") == 3),
                "total_target": sum(item.get("target_judul", 0) for item in data),
            }
            
            log.debug(f"Laporan harian by joki: {len(data)} tasks")
            
            return HarianResult.ok(data, tanggal, stats)
            
        except Exception as e:
            log.error(f"Failed to get laporan harian by joki: {e}")
            return HarianResult.error(f"Gagal mengambil laporan: {str(e)}")

    @staticmethod
    def execute_by_kloter(
        tanggal: Optional[date] = None,
        kloter_id: Optional[int] = None,
    ) -> HarianResult:
        """
        Mendapatkan laporan harian untuk kloter tertentu.
        
        Args:
            tanggal: Tanggal laporan (default: hari ini)
            kloter_id: ID kloter (wajib)
            
        Returns:
            HarianResult: Laporan harian kloter
        """
        if kloter_id is None:
            return HarianResult.error("Kloter ID wajib diisi.")
        
        if tanggal is None:
            tanggal = date.today()
        
        log.info(f"Get laporan harian by kloter: tanggal={tanggal}, kloter_id={kloter_id}")
        
        try:
            data = PortalJokiLaporanRepository.get_harian_by_kloter(tanggal, kloter_id)
            
            stats = {
                "total": len(data),
                "kloter_id": kloter_id,
                "pending": sum(1 for item in data if item.get("status") == 0),
                "upload": sum(1 for item in data if item.get("status") == 1),
                "revisi": sum(1 for item in data if item.get("status") == 2),
                "selesai": sum(1 for item in data if item.get("status") == 3),
                "total_target": sum(item.get("target_judul", 0) for item in data),
            }
            
            log.debug(f"Laporan harian by kloter: {len(data)} tasks")
            
            return HarianResult.ok(data, tanggal, stats)
            
        except Exception as e:
            log.error(f"Failed to get laporan harian by kloter: {e}")
            return HarianResult.error(f"Gagal mengambil laporan: {str(e)}")

    @staticmethod
    def get_rekap(tanggal: Optional[date] = None) -> Dict[str, Any]:
        """
        Mendapatkan rekap harian.
        
        Args:
            tanggal: Tanggal rekap (default: hari ini)
            
        Returns:
            dict: Rekap harian
        """
        if tanggal is None:
            tanggal = date.today()
        
        log.info(f"Get rekap harian: tanggal={tanggal}")
        
        try:
            rekap = PortalJokiLaporanRepository.get_rekap_harian(tanggal)
            log.debug(f"Rekap harian: {rekap}")
            return rekap or {}
            
        except Exception as e:
            log.error(f"Failed to get rekap harian: {e}")
            return {}

    @staticmethod
    def get_range(
        start_date: date,
        end_date: date,
        joki_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan laporan dalam rentang tanggal.
        
        Args:
            start_date: Tanggal awal
            end_date: Tanggal akhir
            joki_id: Filter by joki (opsional)
            
        Returns:
            List[dict]: Laporan harian per tanggal
        """
        log.info(f"Get laporan range: {start_date} - {end_date}, joki_id={joki_id}")
        
        result = []
        current = start_date
        
        while current <= end_date:
            if joki_id:
                day_result = PortalJokiHarianService.execute_by_joki(current, joki_id)
            else:
                day_result = PortalJokiHarianService.execute(current)
            
            result.append({
                "tanggal": current.isoformat(),
                "total": day_result.total_tasks,
                "pending": day_result.pending,
                "upload": day_result.upload,
                "revisi": day_result.revisi,
                "selesai": day_result.selesai,
                "completion_rate": day_result.completion_rate,
            })
            
            current += timedelta(days=1)
        
        log.debug(f"Laporan range: {len(result)} days")
        return result


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
harian_service = PortalJokiHarianService()