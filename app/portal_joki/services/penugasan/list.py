"""
Portal Joki - List Penugasan Service

Service untuk listing penugasan dengan berbagai filter.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta

from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.portal_joki.repositories.penugasan.kloter_repo import (
    PortalJokiKloterRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class ListPenugasanResult:
    """
    Result object untuk list penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[List[Dict[str, Any]]] = None,
        total: int = 0,
        limit: Optional[int] = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or []
        self.total = total
        self.limit = limit
        self.offset = offset
        self.filters = filters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "total": self.total,
            "limit": self.limit,
            "offset": self.offset,
            "filters": self.filters,
        }
    
    @classmethod
    def ok(
        cls,
        data: List[Dict[str, Any]],
        total: int,
        limit: Optional[int] = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        message: str = "OK",
    ) -> "ListPenugasanResult":
        """Create success result."""
        return cls(True, message, data, total, limit, offset, filters or {})
    
    @classmethod
    def error(
        cls,
        message: str,
    ) -> "ListPenugasanResult":
        """Create error result."""
        return cls(False, message, [], 0)
    
    @property
    def has_more(self) -> bool:
        """Check if there are more items."""
        if self.limit is None:
            return False
        return self.offset + self.limit < self.total


# ==========================================================
# LIST SERVICE
# ==========================================================
class PortalJokiListService:
    """
    Service List Penugasan Portal Joki.
    
    Menyediakan fungsi untuk:
    - List semua penugasan (dengan filter & pagination)
    - List by date
    - List by joki
    - List by joki & date
    - List by kloter
    - List by status
    - List by date range
    - List today
    """

    @staticmethod
    def all(
        limit: Optional[int] = 100,
        offset: int = 0,
        status: Optional[int] = None,
        joki_id: Optional[int] = None,
        kloter_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> ListPenugasanResult:
        """
        List semua penugasan dengan filter.
        
        Args:
            limit: Jumlah data per page
            offset: Offset untuk pagination
            status: Filter by status
            joki_id: Filter by joki
            kloter_id: Filter by kloter
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            search: Search by joki nama/kode
            
        Returns:
            ListPenugasanResult: List penugasan
        """
        log.info(f"List all penugasan: limit={limit}, offset={offset}, status={status}, joki_id={joki_id}")
        
        try:
            # Build filters
            filters = {}
            if status is not None:
                filters["status"] = status
            if joki_id is not None:
                filters["joki_id"] = joki_id
            if start_date:
                filters["start_date"] = start_date
            if end_date:
                filters["end_date"] = end_date
            
            # Get data
            data = PortalJokiPenugasanRepository.get_datatable(
                limit=limit,
                offset=offset,
                status=status,
                joki_id=joki_id,
                start_date=start_date,
                end_date=end_date,
            )
            
            # Add status labels
            for item in data:
                try:
                    # Pastikan item adalah dict
                    if isinstance(item, dict):
                        status = item.get("status", 0)
                        item["status_label"] = PortalJokiPenugasanRepository.get_status_label(status)
                        item["status_color"] = PortalJokiPenugasanRepository.get_status_color(status)
                    else:
                        log.warning(f"Item is not dict: {item}")
                except Exception as e:
                    log.error(f"Error adding status label: {e}")
                    if isinstance(item, dict):
                        item["status_label"] = "Unknown"
                        item["status_color"] = "secondary"
            
            # Get total count
            total = PortalJokiPenugasanRepository.count(
                status=status,
                joki_id=joki_id,
                start_date=start_date,
                end_date=end_date,
            )
            
            log.debug(f"List all: {len(data)} rows, total={total}")
            
            return ListPenugasanResult.ok(
                data=data,
                total=total,
                limit=limit,
                offset=offset,
                filters=filters,
            )
            
        except Exception as e:
            log.error(f"Failed to list penugasan: {e}")
            return ListPenugasanResult.error(f"Gagal mengambil data: {str(e)}")

    @staticmethod
    def by_date(
        tanggal: date,
        joki_id: Optional[int] = None,
    ) -> ListPenugasanResult:
        """
        List penugasan by date.
        
        Args:
            tanggal: Tanggal
            joki_id: Filter by joki (opsional)
            
        Returns:
            ListPenugasanResult: List penugasan
        """
        log.info(f"List by date: tanggal={tanggal}, joki_id={joki_id}")
        
        try:
            data = PortalJokiPenugasanRepository.get_by_date(tanggal, joki_id)
            
            # Add status labels
            for item in data:
                try:
                    # Pastikan item adalah dict
                    if isinstance(item, dict):
                        status = item.get("status", 0)
                        item["status_label"] = PortalJokiPenugasanRepository.get_status_label(status)
                        item["status_color"] = PortalJokiPenugasanRepository.get_status_color(status)
                    else:
                        log.warning(f"Item is not dict: {item}")
                except Exception as e:
                    log.error(f"Error adding status label: {e}")
                    if isinstance(item, dict):
                        item["status_label"] = "Unknown"
                        item["status_color"] = "secondary"
            
            log.debug(f"List by date: {len(data)} rows")
            
            return ListPenugasanResult.ok(
                data=data,
                total=len(data),
                filters={"tanggal": tanggal.isoformat(), "joki_id": joki_id},
            )
            
        except Exception as e:
            log.error(f"Failed to list by date: {e}")
            return ListPenugasanResult.error(f"Gagal mengambil data: {str(e)}")

    @staticmethod
    def by_joki(
        joki_id: int,
        limit: Optional[int] = 50,
        offset: int = 0,
    ) -> ListPenugasanResult:
        """
        List penugasan by joki.
        
        Args:
            joki_id: ID joki
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            ListPenugasanResult: List penugasan
        """
        log.info(f"List by joki: joki_id={joki_id}, limit={limit}, offset={offset}")
        
        try:
            data = PortalJokiPenugasanRepository.get_by_joki(joki_id, limit, offset)
            
            # Add status labels
            for item in data:
                try:
                    # Pastikan item adalah dict
                    if isinstance(item, dict):
                        status = item.get("status", 0)
                        item["status_label"] = PortalJokiPenugasanRepository.get_status_label(status)
                        item["status_color"] = PortalJokiPenugasanRepository.get_status_color(status)
                    else:
                        log.warning(f"Item is not dict: {item}")
                except Exception as e:
                    log.error(f"Error adding status label: {e}")
                    if isinstance(item, dict):
                        item["status_label"] = "Unknown"
                        item["status_color"] = "secondary"
            
            total = PortalJokiPenugasanRepository.count(joki_id=joki_id)
            
            log.debug(f"List by joki: {len(data)} rows, total={total}")
            
            return ListPenugasanResult.ok(
                data=data,
                total=total,
                limit=limit,
                offset=offset,
                filters={"joki_id": joki_id},
            )
            
        except Exception as e:
            log.error(f"Failed to list by joki: {e}")
            return ListPenugasanResult.error(f"Gagal mengambil data: {str(e)}")

    @staticmethod
    def by_joki_date(
        joki_id: int,
        tanggal: date,
    ) -> ListPenugasanResult:
        """
        List penugasan by joki and date.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal
            
        Returns:
            ListPenugasanResult: List penugasan
        """
        log.info(f"List by joki date: joki_id={joki_id}, tanggal={tanggal}")
        
        try:
            data = PortalJokiPenugasanRepository.get_by_joki_date(joki_id, tanggal)
            
            # Add status labels
            for item in data:
                try:
                    # Pastikan item adalah dict
                    if isinstance(item, dict):
                        status = item.get("status", 0)
                        item["status_label"] = PortalJokiPenugasanRepository.get_status_label(status)
                        item["status_color"] = PortalJokiPenugasanRepository.get_status_color(status)
                    else:
                        log.warning(f"Item is not dict: {item}")
                except Exception as e:
                    log.error(f"Error adding status label: {e}")
                    if isinstance(item, dict):
                        item["status_label"] = "Unknown"
                        item["status_color"] = "secondary"
            
            log.debug(f"List by joki date: {len(data)} rows")
            
            return ListPenugasanResult.ok(
                data=data,
                total=len(data),
                filters={"joki_id": joki_id, "tanggal": tanggal.isoformat()},
            )
            
        except Exception as e:
            log.error(f"Failed to list by joki date: {e}")
            return ListPenugasanResult.error(f"Gagal mengambil data: {str(e)}")

    @staticmethod
    def by_kloter(
        kloter_id: int,
        tanggal: Optional[date] = None,
    ) -> ListPenugasanResult:
        """
        List penugasan by kloter.
        
        Args:
            kloter_id: ID kloter
            tanggal: Filter by tanggal (opsional)
            
        Returns:
            ListPenugasanResult: List penugasan
        """
        log.info(f"List by kloter: kloter_id={kloter_id}, tanggal={tanggal}")
        
        try:
            data = PortalJokiPenugasanRepository.get_by_kloter(kloter_id, tanggal)
            
            # Add status labels
            for item in data:
                try:
                    # Pastikan item adalah dict
                    if isinstance(item, dict):
                        status = item.get("status", 0)
                        item["status_label"] = PortalJokiPenugasanRepository.get_status_label(status)
                        item["status_color"] = PortalJokiPenugasanRepository.get_status_color(status)
                    else:
                        log.warning(f"Item is not dict: {item}")
                except Exception as e:
                    log.error(f"Error adding status label: {e}")
                    if isinstance(item, dict):
                        item["status_label"] = "Unknown"
                        item["status_color"] = "secondary"
            
            log.debug(f"List by kloter: {len(data)} rows")
            
            return ListPenugasanResult.ok(
                data=data,
                total=len(data),
                filters={"kloter_id": kloter_id, "tanggal": tanggal.isoformat() if tanggal else None},
            )
            
        except Exception as e:
            log.error(f"Failed to list by kloter: {e}")
            return ListPenugasanResult.error(f"Gagal mengambil data: {str(e)}")

    @staticmethod
    def by_status(
        status: int,
        tanggal: Optional[date] = None,
        limit: Optional[int] = 100,
        offset: int = 0,
    ) -> ListPenugasanResult:
        """
        List penugasan by status.
        
        Args:
            status: Status (0-3)
            tanggal: Filter by tanggal (opsional)
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            ListPenugasanResult: List penugasan
        """
        log.info(f"List by status: status={status}, tanggal={tanggal}")
        
        try:
            data = PortalJokiPenugasanRepository.get_by_status(status, tanggal)
            
            # Add status labels
            for item in data:
                try:
                    # Pastikan item adalah dict
                    if isinstance(item, dict):
                        status = item.get("status", 0)
                        item["status_label"] = PortalJokiPenugasanRepository.get_status_label(status)
                        item["status_color"] = PortalJokiPenugasanRepository.get_status_color(status)
                    else:
                        log.warning(f"Item is not dict: {item}")
                except Exception as e:
                    log.error(f"Error adding status label: {e}")
                    if isinstance(item, dict):
                        item["status_label"] = "Unknown"
                        item["status_color"] = "secondary"
            
            total = PortalJokiPenugasanRepository.count(status=status)
            
            log.debug(f"List by status: {len(data)} rows, total={total}")
            
            return ListPenugasanResult.ok(
                data=data,
                total=total,
                limit=limit,
                offset=offset,
                filters={"status": status, "tanggal": tanggal.isoformat() if tanggal else None},
            )
            
        except Exception as e:
            log.error(f"Failed to list by status: {e}")
            return ListPenugasanResult.error(f"Gagal mengambil data: {str(e)}")

    @staticmethod
    def by_date_range(
        start_date: date,
        end_date: date,
        joki_id: Optional[int] = None,
        limit: Optional[int] = 100,
        offset: int = 0,
    ) -> ListPenugasanResult:
        """
        List penugasan by date range.
        
        Args:
            start_date: Tanggal awal
            end_date: Tanggal akhir
            joki_id: Filter by joki (opsional)
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            ListPenugasanResult: List penugasan
        """
        log.info(f"List by date range: {start_date} - {end_date}, joki_id={joki_id}")
        
        try:
            data = PortalJokiPenugasanRepository.get_datatable(
                limit=limit,
                offset=offset,
                joki_id=joki_id,
                start_date=start_date,
                end_date=end_date,
            )
            
            # Add status labels
            for item in data:
                try:
                    # Pastikan item adalah dict
                    if isinstance(item, dict):
                        status = item.get("status", 0)
                        item["status_label"] = PortalJokiPenugasanRepository.get_status_label(status)
                        item["status_color"] = PortalJokiPenugasanRepository.get_status_color(status)
                    else:
                        log.warning(f"Item is not dict: {item}")
                except Exception as e:
                    log.error(f"Error adding status label: {e}")
                    if isinstance(item, dict):
                        item["status_label"] = "Unknown"
                        item["status_color"] = "secondary"
            
            total = PortalJokiPenugasanRepository.count(
                joki_id=joki_id,
                start_date=start_date,
                end_date=end_date,
            )
            
            log.debug(f"List by date range: {len(data)} rows, total={total}")
            
            return ListPenugasanResult.ok(
                data=data,
                total=total,
                limit=limit,
                offset=offset,
                filters={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "joki_id": joki_id,
                },
            )
            
        except Exception as e:
            log.error(f"Failed to list by date range: {e}")
            return ListPenugasanResult.error(f"Gagal mengambil data: {str(e)}")

    @staticmethod
    def today(
        joki_id: Optional[int] = None,
    ) -> ListPenugasanResult:
        """
        List penugasan hari ini.
        
        Args:
            joki_id: Filter by joki (opsional)
            
        Returns:
            ListPenugasanResult: List penugasan hari ini
        """
        today = date.today()
        log.info(f"List today: joki_id={joki_id}")
        
        return PortalJokiListService.by_date(today, joki_id)

    @staticmethod
    def this_week(
        joki_id: Optional[int] = None,
    ) -> ListPenugasanResult:
        """
        List penugasan minggu ini.
        
        Args:
            joki_id: Filter by joki (opsional)
            
        Returns:
            ListPenugasanResult: List penugasan minggu ini
        """
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        
        log.info(f"List this week: {start_date} - {end_date}, joki_id={joki_id}")
        
        return PortalJokiListService.by_date_range(start_date, end_date, joki_id)

    @staticmethod
    def this_month(
        joki_id: Optional[int] = None,
    ) -> ListPenugasanResult:
        """
        List penugasan bulan ini.
        
        Args:
            joki_id: Filter by joki (opsional)
            
        Returns:
            ListPenugasanResult: List penugasan bulan ini
        """
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, 28)
        
        log.info(f"List this month: {start_date} - {end_date}, joki_id={joki_id}")
        
        return PortalJokiListService.by_date_range(start_date, end_date, joki_id)


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
list_service = PortalJokiListService()