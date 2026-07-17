"""
Portal Joki - Delete Penugasan Service

Service untuk menghapus penugasan.
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
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class DeletePenugasanResult:
    """
    Result object untuk delete penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[list] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "warnings": self.warnings,
        }
    
    @classmethod
    def ok(
        cls,
        message: str = "Penugasan berhasil dihapus.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[list] = None,
    ) -> "DeletePenugasanResult":
        """Create success result."""
        return cls(True, message, data or {}, warnings or [])
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "DeletePenugasanResult":
        """Create error result."""
        return cls(False, message, data or {})


# ==========================================================
# DELETE SERVICE
# ==========================================================
class PortalJokiDeleteService:
    """
    Service Delete Penugasan Portal Joki.
    
    Business Flow:
    1. Validasi penugasan exists
    2. Cek apakah sudah memiliki upload/review (warning)
    3. Delete related data (uploads, reviews) jika ada
    4. Delete penugasan
    5. Return result
    """

    @staticmethod
    def execute(
        penugasan_id: int,
        force: bool = False,
        delete_related: bool = True,
    ) -> DeletePenugasanResult:
        """
        Delete penugasan.
        
        Args:
            penugasan_id: ID penugasan
            force: Force delete (skip warnings)
            delete_related: Delete related uploads & reviews
            
        Returns:
            DeletePenugasanResult: Result dengan status
        """
        log.info(f"Delete penugasan: ID={penugasan_id}, force={force}, delete_related={delete_related}")
        
        # ==========================================================
        # 1. CEK DATA
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return DeletePenugasanResult.error(f"Gagal mengambil data penugasan: {str(e)}")
        
        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return DeletePenugasanResult.error("Penugasan tidak ditemukan.")
        
        # Get related data counts
        upload_count = 0
        review_count = 0
        
        try:
            upload_count = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)
            review_count = PortalJokiReviewRepository.count_by_penugasan(penugasan_id)
        except Exception as e:
            log.warning(f"Failed to get related counts: {e}")
        
        # ==========================================================
        # 2. CEK UPLOAD/REVIEW (WARNING)
        # ==========================================================
        warnings = []
        
        if upload_count > 0:
            warnings.append(f"Penugasan memiliki {upload_count} upload. {'Akan dihapus.' if delete_related else 'Tidak dihapus.'}")
        
        if review_count > 0:
            warnings.append(f"Penugasan memiliki {review_count} review. {'Akan dihapus.' if delete_related else 'Tidak dihapus.'}")
        
        # Check if penugasan sudah selesai
        status = penugasan.get("status", 0)
        if status == 3:
            warnings.append("Penugasan sudah selesai. Hapus dengan hati-hati.")
        
        # Check if force is required
        if (upload_count > 0 or review_count > 0) and not force:
            log.warning(f"Penugasan has related data: upload={upload_count}, review={review_count}")
            return DeletePenugasanResult.ok(
                f"Penugasan memiliki data terkait. Gunakan force=True untuk menghapus semua.",
                {
                    "penugasan_id": penugasan_id,
                    "upload_count": upload_count,
                    "review_count": review_count,
                    "status": status,
                },
                warnings,
            )
        
        # ==========================================================
        # 3. HAPUS RELATED DATA
        # ==========================================================
        deleted_uploads = 0
        deleted_reviews = 0
        
        if delete_related:
            try:
                # Delete uploads
                if upload_count > 0:
                    deleted_uploads = PortalJokiUploadRepository.delete_by_penugasan(penugasan_id)
                    log.info(f"Deleted {deleted_uploads} uploads for penugasan_id={penugasan_id}")
                
                # Delete reviews
                if review_count > 0:
                    deleted_reviews = PortalJokiReviewRepository.delete_by_penugasan(penugasan_id)
                    log.info(f"Deleted {deleted_reviews} reviews for penugasan_id={penugasan_id}")
                    
            except Exception as e:
                log.error(f"Failed to delete related data: {e}")
                if not force:
                    return DeletePenugasanResult.error(f"Gagal menghapus data terkait: {str(e)}")
                warnings.append(f"Gagal menghapus data terkait: {str(e)}")
        
        # ==========================================================
        # 4. HAPUS PENUGASAN
        # ==========================================================
        try:
            success = PortalJokiPenugasanRepository.delete(penugasan_id)
            
            if not success:
                log.error(f"Failed to delete penugasan: ID={penugasan_id}")
                return DeletePenugasanResult.error("Gagal menghapus penugasan.")
            
            log.info(f"Penugasan deleted: ID={penugasan_id}")
            
            return DeletePenugasanResult.ok(
                "Penugasan berhasil dihapus.",
                {
                    "penugasan_id": penugasan_id,
                    "tanggal": penugasan.get("tanggal"),
                    "joki_id": penugasan.get("joki_id"),
                    "joki_nama": penugasan.get("joki_nama"),
                    "upload_deleted": deleted_uploads,
                    "review_deleted": deleted_reviews,
                    "warnings_count": len(warnings),
                },
                warnings,
            )
            
        except Exception as e:
            log.error(f"Failed to delete penugasan: {e}")
            return DeletePenugasanResult.error(f"Gagal menghapus penugasan: {str(e)}")

    @staticmethod
    def execute_bulk(
        penugasan_ids: list,
        force: bool = False,
        delete_related: bool = True,
    ) -> Dict[str, Any]:
        """
        Bulk delete multiple penugasan.
        
        Args:
            penugasan_ids: List ID penugasan
            force: Force delete
            delete_related: Delete related data
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk delete penugasan: {len(penugasan_ids)} items")
        
        success_count = 0
        failed_count = 0
        deleted_ids = []
        errors = []
        warnings = []
        total_uploads_deleted = 0
        total_reviews_deleted = 0
        
        for idx, penugasan_id in enumerate(penugasan_ids):
            result = PortalJokiDeleteService.execute(
                penugasan_id=penugasan_id,
                force=force,
                delete_related=delete_related,
            )
            
            if result.success:
                success_count += 1
                deleted_ids.append(penugasan_id)
                if result.data:
                    total_uploads_deleted += result.data.get("upload_deleted", 0)
                    total_reviews_deleted += result.data.get("review_deleted", 0)
                warnings.extend(result.warnings)
            else:
                failed_count += 1
                errors.append({
                    "id": penugasan_id,
                    "error": result.message,
                })
        
        log.info(f"Bulk delete: {success_count} success, {failed_count} failed")
        
        return {
            "success": failed_count == 0,
            "message": f"{success_count} berhasil dihapus, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "deleted_ids": deleted_ids,
            "total_uploads_deleted": total_uploads_deleted,
            "total_reviews_deleted": total_reviews_deleted,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def execute_by_date(
        tanggal: date,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Delete all penugasan on a specific date.
        
        Args:
            tanggal: Tanggal
            force: Force delete
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Delete penugasan by date: {tanggal}, force={force}")
        
        try:
            # Get all penugasan on date
            penugasan_list = PortalJokiPenugasanRepository.get_by_date(tanggal)
            
            if not penugasan_list:
                return {
                    "success": True,
                    "message": f"Tidak ada penugasan pada tanggal {tanggal}.",
                    "deleted_count": 0,
                    "total": 0,
                }
            
            penugasan_ids = [p["id"] for p in penugasan_list]
            
            # Check if any has related data
            has_related = False
            for penugasan in penugasan_list:
                if penugasan.get("status") != 0:
                    has_related = True
                    break
            
            if has_related and not force:
                return {
                    "success": False,
                    "message": f"Terdapat penugasan dengan status bukan pending. Gunakan force=True untuk menghapus semua.",
                    "total": len(penugasan_ids),
                    "penugasan_ids": penugasan_ids,
                }
            
            # Delete all
            result = PortalJokiDeleteService.execute_bulk(
                penugasan_ids,
                force=force,
                delete_related=True,
            )
            
            return {
                "success": result["success"],
                "message": result["message"],
                "deleted_count": result["success_count"],
                "failed_count": result["failed_count"],
                "total": len(penugasan_ids),
                "deleted_ids": result["deleted_ids"],
                "errors": result["errors"],
            }
            
        except Exception as e:
            log.error(f"Failed to delete by date: {e}")
            return {
                "success": False,
                "message": f"Gagal menghapus penugasan: {str(e)}",
                "deleted_count": 0,
                "total": 0,
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
delete_service = PortalJokiDeleteService()