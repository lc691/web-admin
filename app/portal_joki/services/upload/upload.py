"""
Portal Joki - Upload Service

Service untuk upload file penugasan.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import mimetypes

from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
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
class UploadResult:
    """
    Result object untuk upload.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        upload_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ):
        self.success = success
        self.message = message
        self.upload_id = upload_id
        self.data = data or {}
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "upload_id": self.upload_id,
            "data": self.data,
            "warnings": self.warnings,
        }
    
    @classmethod
    def ok(
        cls,
        upload_id: int,
        message: str = "Upload berhasil.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ) -> "UploadResult":
        """Create success result."""
        return cls(True, message, upload_id, data or {}, warnings or [])
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "UploadResult":
        """Create error result."""
        return cls(False, message, None, data or {})


# ==========================================================
# UPLOAD SERVICE
# ==========================================================
class PortalJokiUploadService:
    """
    Service Upload Portal Joki.
    
    Business Flow:
    1. Validasi penugasan exists
    2. Validasi status penugasan (tidak boleh sudah selesai)
    3. Validasi file (type, size, extension)
    4. Get next nomor
    5. Create upload
    6. Update status penugasan ke upload
    7. Log aktivitas
    """

    # Allowed mime types
    ALLOWED_MIME_TYPES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
        "image/bmp": ".bmp",
        "image/tiff": ".tiff",
    }
    
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff"}
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    STATUS_UPLOAD = 1
    STATUS_SELESAI = 3

    @staticmethod
    def execute(
        *,
        penugasan_id: int,
        file_path: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
        nomor: Optional[int] = None,
        catatan: Optional[str] = None,
        auto_update_status: bool = True,
        skip_status_check: bool = False,
    ) -> UploadResult:
        """
        Upload file untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            file_path: Path file yang diupload
            original_filename: Nama file asli
            mime_type: Tipe MIME file
            file_size: Ukuran file dalam bytes
            nomor: Nomor urut upload (auto jika None)
            catatan: Catatan tambahan
            auto_update_status: Auto update status ke upload
            skip_status_check: Skip status validation
            
        Returns:
            UploadResult: Result dengan upload_id
        """
        log.info(f"Upload file: penugasan_id={penugasan_id}, file={original_filename}")

        # ==========================================================
        # 1. VALIDASI PENUGASAN
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return UploadResult.error(f"Gagal mengambil data penugasan: {str(e)}")

        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return UploadResult.error("Penugasan tidak ditemukan.")

        # ==========================================================
        # 2. VALIDASI STATUS
        # ==========================================================
        warnings = []
        current_status = penugasan.get("status", 0)
        
        if not skip_status_check:
            if current_status == PortalJokiUploadService.STATUS_SELESAI:
                log.warning(f"Penugasan already completed: ID={penugasan_id}")
                return UploadResult.error("Penugasan sudah selesai, tidak bisa upload.")
            
            if current_status != PortalJokiUploadService.STATUS_UPLOAD:
                warnings.append(f"Status penugasan akan diubah ke 'upload'.")

        # ==========================================================
        # 3. VALIDASI FILE
        # ==========================================================
        file_path = file_path.strip() if file_path else ""

        if not file_path:
            return UploadResult.error("Screenshot wajib diupload.")

        # Validate mime type
        if not mime_type or not mime_type.startswith("image/"):
            return UploadResult.error("File harus berupa gambar (image/*).")

        # Check if mime type is allowed
        if mime_type not in PortalJokiUploadService.ALLOWED_MIME_TYPES:
            allowed_types = ", ".join(PortalJokiUploadService.ALLOWED_MIME_TYPES.keys())
            return UploadResult.error(f"Tipe file tidak didukung. Gunakan: {allowed_types}")

        # Check file extension
        _, ext = os.path.splitext(original_filename.lower())
        if ext not in PortalJokiUploadService.ALLOWED_EXTENSIONS:
            allowed_exts = ", ".join(PortalJokiUploadService.ALLOWED_EXTENSIONS)
            return UploadResult.error(f"Ekstensi file tidak didukung. Gunakan: {allowed_exts}")

        # Validate file size
        if file_size <= 0:
            return UploadResult.error("File kosong atau tidak valid.")

        if file_size > PortalJokiUploadService.MAX_FILE_SIZE:
            max_size_mb = PortalJokiUploadService.MAX_FILE_SIZE / (1024 * 1024)
            return UploadResult.error(f"Ukuran file maksimal {max_size_mb:.0f} MB.")

        # Minimum file size (1 KB)
        if file_size < 1024:
            warnings.append("Ukuran file sangat kecil, mungkin thumbnail atau file corrupt.")

        # ==========================================================
        # 4. GET NOMOR
        # ==========================================================
        if nomor is None:
            try:
                nomor = PortalJokiUploadRepository.get_next_nomor(penugasan_id)
            except Exception as e:
                log.warning(f"Failed to get next nomor: {e}")
                nomor = 1

        # ==========================================================
        # 5. VALIDASI CATATAN
        # ==========================================================
        if catatan is not None:
            catatan = catatan.strip()
            if catatan and len(catatan) > 500:
                return UploadResult.error("Catatan maksimal 500 karakter.")

        # ==========================================================
        # 6. SAVE UPLOAD
        # ==========================================================
        try:
            upload_id = PortalJokiUploadRepository.create(
                penugasan_id=penugasan_id,
                file_path=file_path,
                original_filename=original_filename,
                mime_type=mime_type,
                file_size=file_size,
                nomor=nomor,
                catatan=catatan,
            )

            if not upload_id:
                log.error(f"Failed to save upload: penugasan_id={penugasan_id}")
                return UploadResult.error("Gagal menyimpan upload.")

            log.info(f"Upload saved: ID={upload_id}, penugasan_id={penugasan_id}")

        except Exception as e:
            log.error(f"Failed to save upload: {e}")
            return UploadResult.error(f"Gagal menyimpan upload: {str(e)}")

        # ==========================================================
        # 7. UPDATE STATUS PENUGASAN
        # ==========================================================
        if auto_update_status and current_status != PortalJokiUploadService.STATUS_UPLOAD:
            try:
                status_updated = PortalJokiProgressService.execute(
                    penugasan_id=penugasan_id,
                    status=PortalJokiUploadService.STATUS_UPLOAD,
                    updated_by="system",
                    force=True,
                )

                if not status_updated.success:
                    log.warning(f"Failed to update status: {status_updated.message}")
                    warnings.append(f"Status penugasan tidak diperbarui: {status_updated.message}")

            except Exception as e:
                log.error(f"Failed to update status: {e}")
                warnings.append(f"Gagal memperbarui status: {str(e)}")

        # ==========================================================
        # 8. RETURN RESULT
        # ==========================================================
        log.info(f"Upload completed: ID={upload_id}, penugasan_id={penugasan_id}")

        return UploadResult.ok(
            upload_id=upload_id,
            message="Upload berhasil.",
            data={
                "penugasan_id": penugasan_id,
                "upload_id": upload_id,
                "nomor": nomor,
                "filename": original_filename,
                "file_size": file_size,
                "file_size_formatted": PortalJokiUploadService._format_file_size(file_size),
                "tanggal": penugasan.get("tanggal"),
                "joki_kode": penugasan.get("joki_kode"),
                "joki_nama": penugasan.get("joki_nama"),
                "timestamp": datetime.now().isoformat(),
            },
            warnings=warnings,
        )

    @staticmethod
    def execute_bulk(
        penugasan_id: int,
        files: List[Dict[str, Any]],
        auto_update_status: bool = True,
    ) -> Dict[str, Any]:
        """
        Bulk upload multiple files for one penugasan.
        
        Args:
            penugasan_id: ID penugasan
            files: List data file [{"file_path": str, "original_filename": str, ...}]
            auto_update_status: Auto update status ke upload
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk upload: penugasan_id={penugasan_id}, {len(files)} files")

        success_count = 0
        failed_count = 0
        upload_ids = []
        errors = []

        for idx, file_data in enumerate(files):
            result = PortalJokiUploadService.execute(
                penugasan_id=penugasan_id,
                auto_update_status=(auto_update_status and idx == 0),
                **file_data,
            )

            if result.success:
                success_count += 1
                upload_ids.append(result.upload_id)
            else:
                failed_count += 1
                errors.append({
                    "index": idx,
                    "filename": file_data.get("original_filename", "unknown"),
                    "error": result.message,
                })

        log.info(f"Bulk upload: {success_count} success, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "message": f"{success_count} file berhasil diupload, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "upload_ids": upload_ids,
            "errors": errors,
        }

    @staticmethod
    def validate_file(
        file_path: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
    ) -> Dict[str, Any]:
        """
        Validate file before upload.
        
        Args:
            file_path: Path file
            original_filename: Nama file asli
            mime_type: Tipe MIME
            file_size: Ukuran file
            
        Returns:
            dict: Validation result
        """
        errors = []
        warnings = []

        # Check file path
        if not file_path or not file_path.strip():
            errors.append("File path tidak valid.")

        # Check mime type
        if not mime_type:
            errors.append("Tipe file tidak terdeteksi.")
        elif not mime_type.startswith("image/"):
            errors.append("File harus berupa gambar (image/*).")
        elif mime_type not in PortalJokiUploadService.ALLOWED_MIME_TYPES:
            allowed_types = ", ".join(PortalJokiUploadService.ALLOWED_MIME_TYPES.keys())
            errors.append(f"Tipe file tidak didukung. Gunakan: {allowed_types}")

        # Check extension
        _, ext = os.path.splitext(original_filename.lower())
        if ext not in PortalJokiUploadService.ALLOWED_EXTENSIONS:
            allowed_exts = ", ".join(PortalJokiUploadService.ALLOWED_EXTENSIONS)
            errors.append(f"Ekstensi file tidak didukung. Gunakan: {allowed_exts}")

        # Check file size
        if file_size <= 0:
            errors.append("File kosong atau tidak valid.")
        elif file_size > PortalJokiUploadService.MAX_FILE_SIZE:
            max_size_mb = PortalJokiUploadService.MAX_FILE_SIZE / (1024 * 1024)
            errors.append(f"Ukuran file maksimal {max_size_mb:.0f} MB.")
        elif file_size < 1024:
            warnings.append("Ukuran file sangat kecil, mungkin thumbnail atau file corrupt.")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "file_type": PortalJokiUploadService._get_file_type(mime_type),
            "file_size_formatted": PortalJokiUploadService._format_file_size(file_size),
        }

    @staticmethod
    def _get_file_type(mime_type: str) -> str:
        """Get file type from mime type."""
        if not mime_type:
            return "unknown"
        
        mime_type = mime_type.lower()
        
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type.startswith("application/pdf"):
            return "pdf"
        else:
            return "other"

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size to human readable."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
        
        return f"{size:.1f} {size_names[i]}"


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
upload_service = PortalJokiUploadService()