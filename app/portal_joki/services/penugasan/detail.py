"""
Portal Joki - Detail Penugasan Service

Service untuk mendapatkan detail penugasan.
"""

from typing import Optional, Dict, Any
from datetime import date, datetime

from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.portal_joki.repositories.upload.upload_repo import (
    PortalJokiUploadRepository,
)
from app.portal_joki.repositories.review.review_repo import (
    PortalJokiReviewRepository,
)
from app.portal_joki.repositories.penugasan.progress_repo import (
    PortalJokiProgressRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class DetailPenugasanResult:
    """
    Result object untuk detail penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        related: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.related = related or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "related": self.related,
        }
    
    @classmethod
    def ok(
        cls,
        data: Dict[str, Any],
        related: Optional[Dict[str, Any]] = None,
        message: str = "OK",
    ) -> "DetailPenugasanResult":
        """Create success result."""
        return cls(True, message, data, related or {})
    
    @classmethod
    def error(
        cls,
        message: str,
    ) -> "DetailPenugasanResult":
        """Create error result."""
        return cls(False, message)
    
    @property
    def penugasan_id(self) -> Optional[int]:
        """Get penugasan ID."""
        return self.data.get("id")
    
    @property
    def status(self) -> int:
        """Get status."""
        return self.data.get("status", 0)
    
    @property
    def status_label(self) -> str:
        """Get status label."""
        status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
        return status_map.get(self.status, "Unknown")
    
    @property
    def joki_nama(self) -> str:
        """Get joki nama."""
        return self.data.get("joki_nama", "")
    
    @property
    def joki_kode(self) -> str:
        """Get joki kode."""
        return self.data.get("joki_kode", "")
    
    @property
    def kloter_nama(self) -> str:
        """Get kloter nama."""
        return self.data.get("kloter_nama", "")
    
    @property
    def is_completed(self) -> bool:
        """Check if completed."""
        return self.status == 3


# ==========================================================
# DETAIL SERVICE
# ==========================================================
class PortalJokiDetailService:
    """
    Service Detail Penugasan Portal Joki.
    
    Menyediakan fungsi untuk:
    - Detail penugasan dengan related data
    - Detail dengan upload history
    - Detail dengan review history
    - Detail dengan progress tracking
    """

    @staticmethod
    def execute(
        penugasan_id: int,
        include_related: bool = True,
        include_history: bool = False,
    ) -> DetailPenugasanResult:
        """
        Get detail penugasan.
        
        Args:
            penugasan_id: ID penugasan
            include_related: Include related data (uploads, reviews)
            include_history: Include full history
            
        Returns:
            DetailPenugasanResult: Detail penugasan
        """
        log.info(f"Get detail penugasan: ID={penugasan_id}, include_related={include_related}")
        
        # ==========================================================
        # 1. GET PENUGASAN DATA
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return DetailPenugasanResult.error(f"Gagal mengambil data penugasan: {str(e)}")
        
        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return DetailPenugasanResult.error("Penugasan tidak ditemukan.")
        
        # ==========================================================
        # 2. GET RELATED DATA
        # ==========================================================
        related = {}
        
        if include_related:
            try:
                # Get uploads
                uploads = PortalJokiUploadRepository.get_by_penugasan(penugasan_id)
                related["uploads"] = uploads
                related["upload_count"] = len(uploads)
                
                # Get latest upload
                latest_upload = PortalJokiUploadRepository.get_latest_by_penugasan(penugasan_id)
                related["latest_upload"] = latest_upload
                
                # Get reviews
                reviews = PortalJokiReviewRepository.get_history(penugasan_id)
                related["reviews"] = reviews
                related["review_count"] = len(reviews)
                
                # Get latest review
                latest_review = PortalJokiReviewRepository.get_latest_review(penugasan_id)
                related["latest_review"] = latest_review
                
                # Get progress stats
                progress_stats = PortalJokiProgressRepository.get_progress_stats(penugasan_id)
                related["progress_stats"] = progress_stats
                
                log.debug(f"Related data: uploads={len(uploads)}, reviews={len(reviews)}")
                
            except Exception as e:
                log.warning(f"Failed to get related data: {e}")
                related["error"] = str(e)
        
        # ==========================================================
        # 3. GET HISTORY (if requested)
        # ==========================================================
        if include_history:
            try:
                upload_history = PortalJokiUploadRepository.get_by_penugasan(penugasan_id)
                review_history = PortalJokiReviewRepository.get_history(penugasan_id)
                related["upload_history"] = upload_history
                related["review_history"] = review_history
            except Exception as e:
                log.warning(f"Failed to get history: {e}")
                related["history_error"] = str(e)
        
        # ==========================================================
        # 4. ADD COMPUTED FIELDS
        # ==========================================================
        # Add status label
        status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
        penugasan["status_label"] = status_map.get(penugasan.get("status", 0), "Unknown")
        
        # Check if has upload
        penugasan["has_upload"] = related.get("upload_count", 0) > 0
        
        # Check if has review
        penugasan["has_review"] = related.get("review_count", 0) > 0
        
        # Calculate days since created
        if penugasan.get("created_at"):
            days = (datetime.now() - penugasan["created_at"]).days
            penugasan["days_since_created"] = days
        
        # Check if overdue
        if penugasan.get("deadline"):
            if penugasan["deadline"] < date.today() and penugasan.get("status") != 3:
                penugasan["is_overdue"] = True
            else:
                penugasan["is_overdue"] = False
        
        log.debug(f"Detail penugasan: ID={penugasan_id}, status={penugasan.get('status_label')}")
        
        return DetailPenugasanResult.ok(penugasan, related)

    @staticmethod
    def execute_with_upload_history(
        penugasan_id: int,
    ) -> Dict[str, Any]:
        """
        Get detail penugasan with full upload history.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Detail dengan upload history
        """
        log.info(f"Get detail with upload history: ID={penugasan_id}")
        
        try:
            data = PortalJokiPenugasanRepository.get_with_upload_history(penugasan_id)
            
            if not data:
                log.warning(f"Penugasan not found: ID={penugasan_id}")
                return {
                    "success": False,
                    "message": "Penugasan tidak ditemukan.",
                }
            
            return {
                "success": True,
                "message": "OK",
                "data": data,
            }
            
        except Exception as e:
            log.error(f"Failed to get detail with upload history: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil data: {str(e)}",
            }

    @staticmethod
    def get_quick_info(
        penugasan_id: int,
    ) -> Dict[str, Any]:
        """
        Get quick info for penugasan (lightweight).
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Quick info
        """
        log.debug(f"Get quick info: ID={penugasan_id}")
        
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
            
            if not penugasan:
                return {
                    "success": False,
                    "message": "Penugasan tidak ditemukan.",
                }
            
            return {
                "success": True,
                "id": penugasan.get("id"),
                "tanggal": penugasan.get("tanggal"),
                "joki_kode": penugasan.get("joki_kode"),
                "joki_nama": penugasan.get("joki_nama"),
                "kloter_nama": penugasan.get("kloter_nama"),
                "status": penugasan.get("status"),
                "status_label": penugasan.get("status_label", "Unknown"),
                "target_judul": penugasan.get("target_judul"),
                "deadline": penugasan.get("deadline"),
                "has_upload": penugasan.get("upload_id") is not None,
            }
            
        except Exception as e:
            log.error(f"Failed to get quick info: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil data: {str(e)}",
            }

    @staticmethod
    def get_by_joki(
        joki_id: int,
        limit: Optional[int] = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get penugasan by joki with pagination.
        
        Args:
            joki_id: ID joki
            limit: Jumlah data
            offset: Offset
            
        Returns:
            dict: List penugasan
        """
        log.info(f"Get penugasan by joki: joki_id={joki_id}, limit={limit}, offset={offset}")
        
        try:
            data = PortalJokiPenugasanRepository.get_by_joki(
                joki_id, limit, offset
            )
            
            # Add status labels
            status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
            for item in data:
                item["status_label"] = status_map.get(item.get("status", 0), "Unknown")
            
            total = PortalJokiPenugasanRepository.count(joki_id=joki_id)
            
            return {
                "success": True,
                "data": data,
                "total": total,
                "limit": limit,
                "offset": offset,
                "joki_id": joki_id,
            }
            
        except Exception as e:
            log.error(f"Failed to get penugasan by joki: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil data: {str(e)}",
                "data": [],
                "total": 0,
            }

    @staticmethod
    def get_by_date(
        tanggal: date,
        joki_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get penugasan by date.
        
        Args:
            tanggal: Tanggal
            joki_id: Filter by joki (opsional)
            
        Returns:
            dict: List penugasan
        """
        log.info(f"Get penugasan by date: tanggal={tanggal}, joki_id={joki_id}")
        
        try:
            data = PortalJokiPenugasanRepository.get_by_date(tanggal, joki_id)
            
            status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
            for item in data:
                item["status_label"] = status_map.get(item.get("status", 0), "Unknown")
            
            return {
                "success": True,
                "data": data,
                "total": len(data),
                "tanggal": tanggal.isoformat(),
                "joki_id": joki_id,
            }
            
        except Exception as e:
            log.error(f"Failed to get penugasan by date: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil data: {str(e)}",
                "data": [],
                "total": 0,
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
detail_service = PortalJokiDetailService()