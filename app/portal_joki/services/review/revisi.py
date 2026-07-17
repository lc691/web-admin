"""
Portal Joki - Revisi Review Service

Service untuk mengirim revisi penugasan.
"""

from typing import Optional, Dict, Any, List
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
class RevisiResult:
    """
    Result object untuk revisi penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        review_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
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
        message: str = "Revisi berhasil dikirim.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ) -> "RevisiResult":
        """Create success result."""
        return cls(True, message, review_id, data or {}, warnings or [])
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "RevisiResult":
        """Create error result."""
        return cls(False, message, None, data or {})


# ==========================================================
# REVISI SERVICE
# ==========================================================
class PortalJokiRevisiService:
    """
    Service Revisi Review Portal Joki.
    
    Business Flow:
    1. Validasi penugasan exists
    2. Validasi komentar wajib diisi
    3. Validasi status penugasan (tidak boleh sudah selesai)
    4. Validasi minimal ada upload
    5. Create review dengan status revisi
    6. Update status penugasan ke revisi
    7. Log aktivitas
    """

    STATUS_REVISI = 2
    STATUS_SELESAI = 3
    STATUS_PENDING = 0

    @staticmethod
    def execute(
        *,
        penugasan_id: int,
        komentar: str,
        reviewed_by: str = "admin",
        skip_upload_check: bool = False,
    ) -> RevisiResult:
        """
        Kirim revisi penugasan.
        
        Args:
            penugasan_id: ID penugasan
            komentar: Komentar revisi (wajib)
            reviewed_by: Nama/ID reviewer
            skip_upload_check: Skip upload validation (admin override)
            
        Returns:
            RevisiResult: Result dengan review_id
        """
        log.info(f"Revisi penugasan: ID={penugasan_id}, reviewed_by={reviewed_by}")

        # ==========================================================
        # 1. VALIDASI PENUGASAN
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return RevisiResult.error(f"Gagal mengambil data penugasan: {str(e)}")

        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return RevisiResult.error("Penugasan tidak ditemukan.")

        # ==========================================================
        # 2. VALIDASI KOMENTAR
        # ==========================================================
        komentar = komentar.strip() if komentar else ""

        if not komentar:
            log.warning(f"Empty comment for revisi: penugasan_id={penugasan_id}")
            return RevisiResult.error("Komentar revisi wajib diisi.")

        if len(komentar) < 5:
            return RevisiResult.error("Komentar revisi minimal 5 karakter.")

        if len(komentar) > 2000:
            return RevisiResult.error("Komentar revisi maksimal 2000 karakter.")

        # ==========================================================
        # 3. VALIDASI STATUS
        # ==========================================================
        current_status = penugasan.get("status", 0)
        
        if current_status == PortalJokiRevisiService.STATUS_SELESAI:
            log.warning(f"Penugasan already completed: ID={penugasan_id}")
            return RevisiResult.error("Penugasan sudah selesai, tidak bisa direvisi.")

        if current_status == PortalJokiRevisiService.STATUS_PENDING:
            warnings = ["Penugasan masih pending, revisi akan mengubah status ke revisi."]
        else:
            warnings = []

        # ==========================================================
        # 4. VALIDASI UPLOAD
        # ==========================================================
        if not skip_upload_check:
            try:
                upload_count = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)
                
                if upload_count == 0:
                    log.warning(f"No upload found for revisi: penugasan_id={penugasan_id}")
                    return RevisiResult.error(
                        "Belum ada upload untuk penugasan ini. Upload terlebih dahulu."
                    )
                    
            except Exception as e:
                log.warning(f"Failed to check uploads: {e}")
                warnings.append("Gagal mengecek upload.")

        # ==========================================================
        # 5. CREATE REVIEW
        # ==========================================================
        try:
            review_id = PortalJokiReviewRepository.create(
                penugasan_id=penugasan_id,
                status=PortalJokiRevisiService.STATUS_REVISI,
                komentar=komentar,
                reviewed_by=reviewed_by,
            )

            if not review_id:
                log.error(f"Failed to create review: penugasan_id={penugasan_id}")
                return RevisiResult.error("Gagal membuat review revisi.")

            log.info(f"Review created: ID={review_id}, penugasan_id={penugasan_id}")

        except Exception as e:
            log.error(f"Failed to create review: {e}")
            return RevisiResult.error(f"Gagal membuat review revisi: {str(e)}")

        # ==========================================================
        # 6. UPDATE STATUS PENUGASAN
        # ==========================================================
        try:
            status_updated = PortalJokiProgressService.execute(
                penugasan_id=penugasan_id,
                status=PortalJokiRevisiService.STATUS_REVISI,
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
        # 7. RETURN RESULT
        # ==========================================================
        log.info(f"Revisi sent: penugasan_id={penugasan_id}, review_id={review_id}")

        return RevisiResult.ok(
            review_id=review_id,
            message="Revisi berhasil dikirim.",
            data={
                "penugasan_id": penugasan_id,
                "review_id": review_id,
                "tanggal": penugasan.get("tanggal"),
                "joki_kode": penugasan.get("joki_kode"),
                "joki_nama": penugasan.get("joki_nama"),
                "reviewed_by": reviewed_by,
                "komentar": komentar,
                "timestamp": datetime.now().isoformat(),
            },
            warnings=warnings,
        )

    @staticmethod
    def execute_bulk(
        penugasan_ids: List[int],
        komentar: str,
        reviewed_by: str = "admin",
        skip_upload_check: bool = False,
    ) -> Dict[str, Any]:
        """
        Bulk revisi multiple penugasan.
        
        Args:
            penugasan_ids: List ID penugasan
            komentar: Komentar revisi (sama untuk semua)
            reviewed_by: Nama/ID reviewer
            skip_upload_check: Skip upload validation
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk revisi: {len(penugasan_ids)} items")

        success_count = 0
        failed_count = 0
        revised_ids = []
        review_ids = []
        errors = []
        warnings = []

        for penugasan_id in penugasan_ids:
            result = PortalJokiRevisiService.execute(
                penugasan_id=penugasan_id,
                komentar=komentar,
                reviewed_by=reviewed_by,
                skip_upload_check=skip_upload_check,
            )

            if result.success:
                success_count += 1
                revised_ids.append(penugasan_id)
                review_ids.append(result.review_id)
                if result.warnings:
                    warnings.extend(result.warnings)
            else:
                failed_count += 1
                errors.append({
                    "penugasan_id": penugasan_id,
                    "error": result.message,
                })

        log.info(f"Bulk revisi: {success_count} success, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "message": f"{success_count} penugasan direvisi, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "revised_ids": revised_ids,
            "review_ids": review_ids,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def check_revisable(
        penugasan_id: int,
    ) -> Dict[str, Any]:
        """
        Check if penugasan can be revised.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Check result
        """
        log.debug(f"Check revisable: penugasan_id={penugasan_id}")

        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)

            if not penugasan:
                return {
                    "revisable": False,
                    "reason": "Penugasan tidak ditemukan.",
                }

            if penugasan.get("status") == PortalJokiRevisiService.STATUS_SELESAI:
                return {
                    "revisable": False,
                    "reason": "Penugasan sudah selesai, tidak bisa direvisi.",
                }

            upload_count = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)

            if upload_count == 0:
                return {
                    "revisable": False,
                    "reason": "Belum ada upload. Upload terlebih dahulu.",
                }

            return {
                "revisable": True,
                "reason": "Penugasan siap untuk direvisi.",
                "upload_count": upload_count,
                "current_status": penugasan.get("status"),
            }

        except Exception as e:
            log.error(f"Failed to check revisable: {e}")
            return {
                "revisable": False,
                "reason": f"Gagal mengecek: {str(e)}",
            }

    @staticmethod
    def get_revisi_history(
        penugasan_id: int,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get revision history for penugasan.
        
        Args:
            penugasan_id: ID penugasan
            limit: Jumlah history yang diambil
            
        Returns:
            dict: Revision history
        """
        log.debug(f"Get revisi history: penugasan_id={penugasan_id}")

        try:
            reviews = PortalJokiReviewRepository.get_history(penugasan_id, limit)

            revisions = []
            for review in reviews:
                if review.get("status") == PortalJokiRevisiService.STATUS_REVISI:
                    revisions.append({
                        "id": review.get("id"),
                        "komentar": review.get("komentar"),
                        "reviewed_by": review.get("reviewed_by"),
                        "reviewed_at": review.get("reviewed_at"),
                    })

            return {
                "success": True,
                "penugasan_id": penugasan_id,
                "total": len(revisions),
                "revisions": revisions,
            }

        except Exception as e:
            log.error(f"Failed to get revisi history: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil history revisi: {str(e)}",
                "revisions": [],
                "total": 0,
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
revisi_service = PortalJokiRevisiService()