"""
Portal Joki - Approve Review Service

Service untuk menyetujui (approve) penugasan.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.portal_joki.repositories.review.review_repo import (
    PortalJokiReviewRepository,
)
from app.portal_joki.repositories.upload.upload_repo import (
    PortalJokiUploadRepository,
)
from app.portal_joki.services.penugasan.progress import (
    PortalJokiProgressService,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class ApproveResult:
    """
    Result object untuk approve penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        review_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[list] = None,
    ):
        self.success = success
        self.message = message
        self.review_id = review_id
        self.data = data or {}
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "review_id": self.review_id,
            "data": self.data,
            "warnings": self.warnings,
        }
    
    @classmethod
    def ok(
        cls,
        review_id: int,
        message: str = "Penugasan berhasil disetujui.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[list] = None,
    ) -> "ApproveResult":
        """Create success result."""
        return cls(True, message, review_id, data or {}, warnings or [])
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ApproveResult":
        """Create error result."""
        return cls(False, message, None, data or {})


# ==========================================================
# APPROVE SERVICE
# ==========================================================
class PortalJokiApproveService:
    """
    Service Approve Review Portal Joki.
    
    Business Flow:
    1. Validasi penugasan exists
    2. Validasi status penugasan (tidak boleh sudah selesai)
    3. Validasi minimal ada upload
    4. Create review dengan status selesai
    5. Update status penugasan ke selesai
    6. Log aktivitas
    """

    STATUS_SELESAI = 3
    STATUS_REVISI = 2

    @staticmethod
    def execute(
        *,
        penugasan_id: int,
        komentar: Optional[str] = None,
        reviewed_by: str = "admin",
        skip_upload_check: bool = False,
    ) -> ApproveResult:
        """
        Approve penugasan.
        
        Args:
            penugasan_id: ID penugasan
            komentar: Komentar review (opsional)
            reviewed_by: Nama/ID reviewer
            skip_upload_check: Skip upload validation (admin override)
            
        Returns:
            ApproveResult: Result dengan review_id
        """
        log.info(f"Approve penugasan: ID={penugasan_id}, reviewed_by={reviewed_by}")

        # ==========================================================
        # 1. VALIDASI PENUGASAN
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return ApproveResult.error(f"Gagal mengambil data penugasan: {str(e)}")

        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return ApproveResult.error("Penugasan tidak ditemukan.")

        # ==========================================================
        # 2. VALIDASI STATUS
        # ==========================================================
        current_status = penugasan.get("status", 0)
        
        if current_status == PortalJokiApproveService.STATUS_SELESAI:
            log.warning(f"Penugasan already completed: ID={penugasan_id}")
            return ApproveResult.error("Penugasan sudah selesai.")

        # ==========================================================
        # 3. VALIDASI UPLOAD
        # ==========================================================
        warnings = []
        
        if not skip_upload_check:
            try:
                upload_count = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)
                
                if upload_count == 0:
                    log.warning(f"No upload found for penugasan: ID={penugasan_id}")
                    return ApproveResult.error(
                        "Belum ada upload untuk penugasan ini. Upload terlebih dahulu."
                    )
                
                if upload_count < 1:
                    warnings.append(f"Minimal upload: {upload_count} upload ditemukan.")
                    
            except Exception as e:
                log.warning(f"Failed to check uploads: {e}")
                warnings.append("Gagal mengecek upload.")

        # ==========================================================
        # 4. CREATE REVIEW
        # ==========================================================
        try:
            review_id = PortalJokiReviewRepository.create(
                penugasan_id=penugasan_id,
                status=PortalJokiApproveService.STATUS_SELESAI,
                komentar=komentar,
                reviewed_by=reviewed_by,
            )

            if not review_id:
                log.error(f"Failed to create review: penugasan_id={penugasan_id}")
                return ApproveResult.error("Gagal membuat review.")

            log.info(f"Review created: ID={review_id}, penugasan_id={penugasan_id}")

        except Exception as e:
            log.error(f"Failed to create review: {e}")
            return ApproveResult.error(f"Gagal membuat review: {str(e)}")

        # ==========================================================
        # 5. UPDATE STATUS PENUGASAN
        # ==========================================================
        try:
            status_updated = PortalJokiProgressService.execute(
                penugasan_id=penugasan_id,
                status=PortalJokiApproveService.STATUS_SELESAI,
                updated_by=reviewed_by,
                force=True,
            )

            if not status_updated.success:
                log.warning(f"Failed to update status: {status_updated.message}")
                warnings.append(f"Status penugasan tidak diperbarui: {status_updated.message}")

        except Exception as e:
            log.error(f"Failed to update status: {e}")
            warnings.append(f"Gagal memperbarui status: {str(e)}")

        # ==========================================================
        # 6. RETURN RESULT
        # ==========================================================
        log.info(f"Penugasan approved: ID={penugasan_id}, review_id={review_id}")

        return ApproveResult.ok(
            review_id=review_id,
            message="Penugasan berhasil disetujui.",
            data={
                "penugasan_id": penugasan_id,
                "review_id": review_id,
                "tanggal": penugasan.get("tanggal"),
                "joki_kode": penugasan.get("joki_kode"),
                "joki_nama": penugasan.get("joki_nama"),
                "reviewed_by": reviewed_by,
                "timestamp": datetime.now().isoformat(),
            },
            warnings=warnings,
        )

    @staticmethod
    def execute_bulk(
        penugasan_ids: list,
        reviewed_by: str = "admin",
        komentar: Optional[str] = None,
        skip_upload_check: bool = False,
    ) -> Dict[str, Any]:
        """
        Bulk approve multiple penugasan.
        
        Args:
            penugasan_ids: List ID penugasan
            reviewed_by: Nama/ID reviewer
            komentar: Komentar (sama untuk semua)
            skip_upload_check: Skip upload validation
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk approve: {len(penugasan_ids)} items")

        success_count = 0
        failed_count = 0
        approved_ids = []
        review_ids = []
        errors = []
        warnings = []

        for penugasan_id in penugasan_ids:
            result = PortalJokiApproveService.execute(
                penugasan_id=penugasan_id,
                komentar=komentar,
                reviewed_by=reviewed_by,
                skip_upload_check=skip_upload_check,
            )

            if result.success:
                success_count += 1
                approved_ids.append(penugasan_id)
                review_ids.append(result.review_id)
                if result.warnings:
                    warnings.extend(result.warnings)
            else:
                failed_count += 1
                errors.append({
                    "penugasan_id": penugasan_id,
                    "error": result.message,
                })

        log.info(f"Bulk approve: {success_count} success, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "message": f"{success_count} penugasan berhasil disetujui, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "approved_ids": approved_ids,
            "review_ids": review_ids,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def check_approvable(
        penugasan_id: int,
    ) -> Dict[str, Any]:
        """
        Check if penugasan can be approved.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Check result
        """
        log.debug(f"Check approvable: penugasan_id={penugasan_id}")

        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)

            if not penugasan:
                return {
                    "approvable": False,
                    "reason": "Penugasan tidak ditemukan.",
                }

            if penugasan.get("status") == PortalJokiApproveService.STATUS_SELESAI:
                return {
                    "approvable": False,
                    "reason": "Penugasan sudah selesai.",
                }

            upload_count = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)

            if upload_count == 0:
                return {
                    "approvable": False,
                    "reason": "Belum ada upload. Upload terlebih dahulu.",
                }

            return {
                "approvable": True,
                "reason": "Penugasan siap untuk disetujui.",
                "upload_count": upload_count,
                "current_status": penugasan.get("status"),
            }

        except Exception as e:
            log.error(f"Failed to check approvable: {e}")
            return {
                "approvable": False,
                "reason": f"Gagal mengecek: {str(e)}",
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
approve_service = PortalJokiApproveService()