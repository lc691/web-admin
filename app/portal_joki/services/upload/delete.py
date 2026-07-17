"""
Portal Joki - Delete Upload Service

Service untuk menghapus upload file penugasan.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import os

from app.portal_joki.repositories.upload.upload_repo import (
    PortalJokiUploadRepository,
)
from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.portal_joki.services.penugasan.progress import (
    PortalJokiProgressService,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class DeleteUploadResult:
    """
    Result object untuk delete upload.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
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
        message: str = "Upload berhasil dihapus.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ) -> "DeleteUploadResult":
        """Create success result."""
        return cls(True, message, data or {}, warnings or [])
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "DeleteUploadResult":
        """Create error result."""
        return cls(False, message, data or {})


# ==========================================================
# DELETE UPLOAD SERVICE
# ==========================================================
class PortalJokiDeleteUploadService:
    """
    Service Delete Upload Portal Joki.
    
    Business Flow:
    1. Validasi upload exists
    2. Hapus file dari database
    3. Cek sisa upload
    4. Update status penugasan jika tidak ada upload
    5. Log aktivitas
    """

    @staticmethod
    def execute(
        upload_id: int,
        delete_physical_file: bool = False,
        auto_update_status: bool = True,
    ) -> DeleteUploadResult:
        """
        Delete upload.
        
        Args:
            upload_id: ID upload
            delete_physical_file: Delete file from storage
            auto_update_status: Auto update status penugasan
            
        Returns:
            DeleteUploadResult: Result status
        """
        log.info(f"Delete upload: ID={upload_id}, delete_physical_file={delete_physical_file}")

        # ==========================================================
        # 1. CEK UPLOAD
        # ==========================================================
        try:
            upload = PortalJokiUploadRepository.get(upload_id)
        except Exception as e:
            log.error(f"Failed to get upload: {e}")
            return DeleteUploadResult.error(f"Gagal mengambil data upload: {str(e)}")

        if not upload:
            log.warning(f"Upload not found: ID={upload_id}")
            return DeleteUploadResult.error("Upload tidak ditemukan.")

        penugasan_id = upload.get("penugasan_id")
        file_path = upload.get("file_path", "")
        original_filename = upload.get("original_filename", "")

        warnings = []

        # ==========================================================
        # 2. HAPUS FILE PHYSICAL (optional)
        # ==========================================================
        if delete_physical_file and file_path:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    log.info(f"Physical file deleted: {file_path}")
                else:
                    warnings.append(f"File tidak ditemukan di storage: {file_path}")
            except Exception as e:
                log.warning(f"Failed to delete physical file: {e}")
                warnings.append(f"Gagal menghapus file fisik: {str(e)}")

        # ==========================================================
        # 3. HAPUS DARI DATABASE
        # ==========================================================
        try:
            success = PortalJokiUploadRepository.delete(upload_id)

            if not success:
                log.error(f"Failed to delete upload: ID={upload_id}")
                return DeleteUploadResult.error("Gagal menghapus upload dari database.")

            log.info(f"Upload deleted from database: ID={upload_id}")

        except Exception as e:
            log.error(f"Failed to delete upload: {e}")
            return DeleteUploadResult.error(f"Gagal menghapus upload: {str(e)}")

        # ==========================================================
        # 4. CEK SISA UPLOAD & UPDATE STATUS
        # ==========================================================
        if auto_update_status and penugasan_id:
            try:
                total_upload = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)
                
                # Jika tidak ada upload lagi, update status ke pending
                if total_upload == 0:
                    log.info(f"No uploads left for penugasan_id={penugasan_id}, updating status to pending")
                    
                    status_updated = PortalJokiProgressService.execute(
                        penugasan_id=penugasan_id,
                        status=0,  # Pending
                        updated_by="system",
                        force=True,
                    )
                    
                    if not status_updated.success:
                        log.warning(f"Failed to update status: {status_updated.message}")
                        warnings.append(f"Status penugasan tidak diperbarui: {status_updated.message}")
                    else:
                        log.info(f"Status updated to pending for penugasan_id={penugasan_id}")
                else:
                    log.debug(f"{total_upload} uploads remaining for penugasan_id={penugasan_id}")

            except Exception as e:
                log.error(f"Failed to check remaining uploads: {e}")
                warnings.append(f"Gagal mengecek sisa upload: {str(e)}")

        # ==========================================================
        # 5. RETURN RESULT
        # ==========================================================
        log.info(f"Upload deleted: ID={upload_id}, penugasan_id={penugasan_id}")

        return DeleteUploadResult.ok(
            message="Upload berhasil dihapus.",
            data={
                "upload_id": upload_id,
                "penugasan_id": penugasan_id,
                "filename": original_filename,
                "file_path": file_path,
                "deleted_at": datetime.now().isoformat(),
                "physical_file_deleted": delete_physical_file,
            },
            warnings=warnings,
        )

    @staticmethod
    def execute_bulk(
        upload_ids: List[int],
        delete_physical_file: bool = False,
        auto_update_status: bool = True,
    ) -> Dict[str, Any]:
        """
        Bulk delete multiple uploads.
        
        Args:
            upload_ids: List ID upload
            delete_physical_file: Delete file from storage
            auto_update_status: Auto update status penugasan
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk delete uploads: {len(upload_ids)} items")

        success_count = 0
        failed_count = 0
        deleted_ids = []
        errors = []
        warnings = []

        for upload_id in upload_ids:
            result = PortalJokiDeleteUploadService.execute(
                upload_id=upload_id,
                delete_physical_file=delete_physical_file,
                auto_update_status=auto_update_status,
            )

            if result.success:
                success_count += 1
                deleted_ids.append(upload_id)
                if result.warnings:
                    warnings.extend(result.warnings)
            else:
                failed_count += 1
                errors.append({
                    "upload_id": upload_id,
                    "error": result.message,
                })

        log.info(f"Bulk delete: {success_count} success, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "message": f"{success_count} upload berhasil dihapus, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "deleted_ids": deleted_ids,
            "errors": errors,
            "warnings": warnings,
        }

    @staticmethod
    def delete_by_penugasan(
        penugasan_id: int,
        delete_physical_file: bool = False,
        auto_update_status: bool = True,
    ) -> Dict[str, Any]:
        """
        Delete all uploads for a penugasan.
        
        Args:
            penugasan_id: ID penugasan
            delete_physical_file: Delete file from storage
            auto_update_status: Auto update status penugasan
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Delete uploads by penugasan: penugasan_id={penugasan_id}")

        try:
            # Get all uploads
            uploads = PortalJokiUploadRepository.get_by_penugasan(penugasan_id)
            
            if not uploads:
                return {
                    "success": True,
                    "message": f"Tidak ada upload untuk penugasan ID={penugasan_id}.",
                    "deleted_count": 0,
                    "total": 0,
                }

            upload_ids = [u["id"] for u in uploads]

            # Delete all
            result = PortalJokiDeleteUploadService.execute_bulk(
                upload_ids=upload_ids,
                delete_physical_file=delete_physical_file,
                auto_update_status=auto_update_status,
            )

            return {
                "success": result["success"],
                "message": result["message"],
                "deleted_count": result["success_count"],
                "failed_count": result["failed_count"],
                "total": len(upload_ids),
                "deleted_ids": result["deleted_ids"],
                "errors": result["errors"],
                "warnings": result["warnings"],
            }

        except Exception as e:
            log.error(f"Failed to delete uploads by penugasan: {e}")
            return {
                "success": False,
                "message": f"Gagal menghapus upload: {str(e)}",
                "deleted_count": 0,
                "total": 0,
            }

    @staticmethod
    def check_deletable(
        upload_id: int,
    ) -> Dict[str, Any]:
        """
        Check if upload can be deleted.
        
        Args:
            upload_id: ID upload
            
        Returns:
            dict: Check result
        """
        log.debug(f"Check deletable: upload_id={upload_id}")

        try:
            upload = PortalJokiUploadRepository.get(upload_id)

            if not upload:
                return {
                    "deletable": False,
                    "reason": "Upload tidak ditemukan.",
                }

            # Get penugasan status
            penugasan = PortalJokiPenugasanRepository.get(upload.get("penugasan_id"))
            
            if penugasan and penugasan.get("status") == 3:
                return {
                    "deletable": False,
                    "reason": "Penugasan sudah selesai, tidak bisa menghapus upload.",
                }

            return {
                "deletable": True,
                "reason": "Upload siap untuk dihapus.",
                "upload": {
                    "id": upload.get("id"),
                    "filename": upload.get("original_filename"),
                    "penugasan_id": upload.get("penugasan_id"),
                },
            }

        except Exception as e:
            log.error(f"Failed to check deletable: {e}")
            return {
                "deletable": False,
                "reason": f"Gagal mengecek: {str(e)}",
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
delete_upload_service = PortalJokiDeleteUploadService()