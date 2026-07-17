"""
Portal Joki - Progress Penugasan Service

Service untuk mengupdate status/progress penugasan.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

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
class ProgressPenugasanResult:
    """
    Result object untuk progress penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        status: Optional[int] = None,
        old_status: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ):
        self.success = success
        self.message = message
        self.status = status
        self.old_status = old_status
        self.data = data or {}
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "status": self.status,
            "old_status": self.old_status,
            "data": self.data,
            "warnings": self.warnings,
        }
    
    @classmethod
    def ok(
        cls,
        status: int,
        old_status: Optional[int] = None,
        message: str = "Status berhasil diperbarui.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ) -> "ProgressPenugasanResult":
        """Create success result."""
        return cls(True, message, status, old_status, data or {}, warnings or [])
    
    @classmethod
    def error(
        cls,
        message: str,
        status: Optional[int] = None,
        warnings: Optional[List[str]] = None,
    ) -> "ProgressPenugasanResult":
        """Create error result."""
        return cls(False, message, status, None, {}, warnings or [])
    
    @property
    def status_label(self) -> str:
        """Get status label."""
        status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
        return status_map.get(self.status, "Unknown")


# ==========================================================
# PROGRESS SERVICE
# ==========================================================
class PortalJokiProgressService:
    """
    Service Progress Penugasan Portal Joki.
    
    Business Flow:
    1. Validasi status
    2. Validasi penugasan exists
    3. Validasi flow status (tidak boleh skip)
    4. Update status
    5. Log perubahan
    """

    # Status constants
    STATUS_PENDING = 0
    STATUS_UPLOAD = 1
    STATUS_REVISI = 2
    STATUS_SELESAI = 3

    STATUS_LABELS = {
        0: "Pending",
        1: "Upload",
        2: "Revisi",
        3: "Selesai",
    }

    STATUS_COLORS = {
        0: "warning",
        1: "info",
        2: "danger",
        3: "success",
    }

    VALID_STATUS = (STATUS_PENDING, STATUS_UPLOAD, STATUS_REVISI, STATUS_SELESAI)

    # Flow yang valid untuk progress
    FLOW_ALLOWED = {
        STATUS_PENDING: [STATUS_UPLOAD, STATUS_REVISI],
        STATUS_UPLOAD: [STATUS_REVISI, STATUS_SELESAI],
        STATUS_REVISI: [STATUS_UPLOAD, STATUS_SELESAI],
        STATUS_SELESAI: [],  # Tidak bisa berubah dari selesai
    }

    @staticmethod
    def execute(
        penugasan_id: int,
        status: int,
        updated_by: Optional[str] = None,
        force: bool = False,
    ) -> ProgressPenugasanResult:
        """
        Update status penugasan.
        
        Args:
            penugasan_id: ID penugasan
            status: Status baru (0-3)
            updated_by: Pengupdate (opsional)
            force: Force update (skip flow validation)
            
        Returns:
            ProgressPenugasanResult: Result dengan status
        """
        log.info(f"Update progress: penugasan_id={penugasan_id}, status={status}, force={force}")

        # ==========================================================
        # 1. VALIDASI STATUS
        # ==========================================================
        if status not in PortalJokiProgressService.VALID_STATUS:
            log.warning(f"Invalid status: {status}")
            return ProgressPenugasanResult.error(
                f"Status tidak valid. Gunakan: {', '.join(map(str, PortalJokiProgressService.VALID_STATUS))}"
            )

        # ==========================================================
        # 2. CEK PENUGASAN
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return ProgressPenugasanResult.error(f"Gagal mengambil data penugasan: {str(e)}")

        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return ProgressPenugasanResult.error("Penugasan tidak ditemukan.")

        old_status = penugasan.get("status", 0)
        old_status_label = PortalJokiProgressService.STATUS_LABELS.get(old_status, "Unknown")

        # ==========================================================
        # 3. TIDAK ADA PERUBAHAN
        # ==========================================================
        if old_status == status:
            log.debug(f"Status unchanged: penugasan_id={penugasan_id}, status={status}")
            return ProgressPenugasanResult.ok(
                status=status,
                old_status=old_status,
                message="Status tidak berubah.",
                data={
                    "penugasan_id": penugasan_id,
                    "status": status,
                    "status_label": PortalJokiProgressService.STATUS_LABELS.get(status),
                },
            )

        # ==========================================================
        # 4. VALIDASI FLOW
        # ==========================================================
        warnings = []
        
        if not force:
            allowed_next = PortalJokiProgressService.FLOW_ALLOWED.get(old_status, [])
            
            if status not in allowed_next:
                allowed_str = ", ".join([PortalJokiProgressService.STATUS_LABELS.get(s, str(s)) for s in allowed_next])
                log.warning(f"Invalid flow: {old_status_label} -> {PortalJokiProgressService.STATUS_LABELS.get(status)}")
                return ProgressPenugasanResult.error(
                    f"Tidak dapat mengubah dari '{old_status_label}' ke '{PortalJokiProgressService.STATUS_LABELS.get(status)}'. "
                    f"Flow yang valid: {allowed_str}",
                    status=status,
                )

        # ==========================================================
        # 5. VALIDASI KHUSUS
        # ==========================================================
        
        # Cek jika mau mark selesai tapi belum ada upload
        if status == PortalJokiProgressService.STATUS_SELESAI:
            try:
                upload_count = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)
                if upload_count == 0:
                    warnings.append("Penugasan ditandai selesai tanpa ada upload.")
            except Exception as e:
                log.warning(f"Failed to check uploads: {e}")

        # Cek jika mau revisi tapi belum ada upload/review
        if status == PortalJokiProgressService.STATUS_REVISI:
            try:
                upload_count = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)
                if upload_count == 0:
                    warnings.append("Penugasan direvisi tanpa ada upload sebelumnya.")
            except Exception as e:
                log.warning(f"Failed to check uploads: {e}")

        # ==========================================================
        # 6. UPDATE STATUS
        # ==========================================================
        try:
            success = PortalJokiPenugasanRepository.update_status(
                penugasan_id,
                status,
            )
            
            if not success:
                log.error(f"Failed to update status: penugasan_id={penugasan_id}")
                return ProgressPenugasanResult.error("Gagal memperbarui status.")

            log.info(f"Status updated: penugasan_id={penugasan_id}, {old_status_label} -> {PortalJokiProgressService.STATUS_LABELS.get(status)}")

            return ProgressPenugasanResult.ok(
                status=status,
                old_status=old_status,
                message=f"Status berhasil diperbarui dari '{old_status_label}' ke '{PortalJokiProgressService.STATUS_LABELS.get(status)}'.",
                data={
                    "penugasan_id": penugasan_id,
                    "status": status,
                    "old_status": old_status,
                    "status_label": PortalJokiProgressService.STATUS_LABELS.get(status),
                    "old_status_label": old_status_label,
                    "updated_by": updated_by,
                },
                warnings=warnings,
            )

        except Exception as e:
            log.error(f"Failed to update progress: {e}")
            return ProgressPenugasanResult.error(f"Gagal memperbarui status: {str(e)}")

    @staticmethod
    def execute_bulk(
        penugasan_ids: List[int],
        status: int,
        updated_by: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Bulk update status penugasan.
        
        Args:
            penugasan_ids: List ID penugasan
            status: Status baru
            updated_by: Pengupdate
            force: Force update
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk update progress: {len(penugasan_ids)} items, status={status}")

        success_count = 0
        failed_count = 0
        updated_ids = []
        errors = []
        warnings = []

        for penugasan_id in penugasan_ids:
            result = PortalJokiProgressService.execute(
                penugasan_id=penugasan_id,
                status=status,
                updated_by=updated_by,
                force=force,
            )

            if result.success:
                success_count += 1
                updated_ids.append(penugasan_id)
                if result.warnings:
                    warnings.extend(result.warnings)
            else:
                failed_count += 1
                errors.append({
                    "id": penugasan_id,
                    "error": result.message,
                })

        log.info(f"Bulk update: {success_count} success, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "message": f"{success_count} berhasil diupdate, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "updated_ids": updated_ids,
            "status": status,
            "status_label": PortalJokiProgressService.STATUS_LABELS.get(status),
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def get_status_label(status: int) -> str:
        """Get status label."""
        return PortalJokiProgressService.STATUS_LABELS.get(status, "Unknown")

    @staticmethod
    def get_status_color(status: int) -> str:
        """Get status color for UI."""
        return PortalJokiProgressService.STATUS_COLORS.get(status, "secondary")

    @staticmethod
    def can_transition(
        from_status: int,
        to_status: int,
    ) -> bool:
        """Check if status transition is allowed."""
        if from_status == to_status:
            return True
        allowed = PortalJokiProgressService.FLOW_ALLOWED.get(from_status, [])
        return to_status in allowed

    @staticmethod
    def get_allowed_next_statuses(
        current_status: int,
    ) -> List[int]:
        """Get allowed next statuses."""
        return PortalJokiProgressService.FLOW_ALLOWED.get(current_status, [])

    @staticmethod
    def get_statuses_with_labels() -> List[Dict[str, Any]]:
        """Get all statuses with labels and colors."""
        return [
            {
                "value": status,
                "label": PortalJokiProgressService.STATUS_LABELS.get(status),
                "color": PortalJokiProgressService.STATUS_COLORS.get(status),
            }
            for status in PortalJokiProgressService.VALID_STATUS
        ]


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
progress_service = PortalJokiProgressService()