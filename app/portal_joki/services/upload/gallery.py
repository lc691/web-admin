"""
Portal Joki - Gallery Service

Service untuk menampilkan gallery upload portal joki.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta

from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.portal_joki.repositories.upload.upload_repo import (
    PortalJokiUploadRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class GalleryResult:
    """
    Result object untuk gallery.
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
        stats: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or []
        self.total = total
        self.limit = limit
        self.offset = offset
        self.filters = filters or {}
        self.stats = stats or {}
    
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
            "stats": self.stats,
        }
    
    @classmethod
    def ok(
        cls,
        data: List[Dict[str, Any]],
        total: int,
        limit: Optional[int] = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        stats: Optional[Dict[str, Any]] = None,
        message: str = "OK",
    ) -> "GalleryResult":
        """Create success result."""
        return cls(True, message, data, total, limit, offset, filters or {}, stats or {})
    
    @classmethod
    def error(
        cls,
        message: str,
    ) -> "GalleryResult":
        """Create error result."""
        return cls(False, message, [], 0)
    
    @property
    def has_more(self) -> bool:
        """Check if there are more items."""
        if self.limit is None:
            return False
        return self.offset + self.limit < self.total
    
    @property
    def total_size(self) -> int:
        """Total file size in bytes."""
        return sum(item.get("file_size", 0) for item in self.data)


# ==========================================================
# GALLERY SERVICE
# ==========================================================
class PortalJokiGalleryService:
    """
    Service Gallery Portal Joki.
    
    Menyediakan fungsi untuk:
    - Gallery by penugasan
    - Gallery by joki
    - Gallery all (admin)
    - Gallery with pagination & filtering
    - Gallery stats
    """

    @staticmethod
    def by_penugasan(
        penugasan_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> GalleryResult:
        """
        Get gallery uploads by penugasan.
        
        Args:
            penugasan_id: ID penugasan
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            GalleryResult: Gallery data
        """
        log.info(f"Get gallery by penugasan: penugasan_id={penugasan_id}")

        # ==========================================================
        # 1. VALIDASI PENUGASAN
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return GalleryResult.error(f"Gagal mengambil data penugasan: {str(e)}")

        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return GalleryResult.error("Penugasan tidak ditemukan.")

        # ==========================================================
        # 2. GET UPLOADS
        # ==========================================================
        try:
            uploads = PortalJokiUploadRepository.get_by_penugasan(
                penugasan_id, limit, offset
            )
            
            total = PortalJokiUploadRepository.count_by_penugasan(penugasan_id)

            # Enrich data
            for upload in uploads:
                upload["file_type"] = PortalJokiGalleryService._get_file_type(
                    upload.get("mime_type", "")
                )
                upload["file_size_formatted"] = PortalJokiGalleryService._format_file_size(
                    upload.get("file_size", 0)
                )

            log.debug(f"Gallery by penugasan: {len(uploads)} uploads, total={total}")

            return GalleryResult.ok(
                data=uploads,
                total=total,
                limit=limit,
                offset=offset,
                filters={"penugasan_id": penugasan_id},
                stats={
                    "penugasan_tanggal": penugasan.get("tanggal"),
                    "joki_kode": penugasan.get("joki_kode"),
                    "joki_nama": penugasan.get("joki_nama"),
                },
            )

        except Exception as e:
            log.error(f"Failed to get gallery by penugasan: {e}")
            return GalleryResult.error(f"Gagal mengambil gallery: {str(e)}")

    @staticmethod
    def by_joki(
        joki_id: int,
        limit: Optional[int] = 50,
        offset: int = 0,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> GalleryResult:
        """
        Get gallery uploads by joki.
        
        Args:
            joki_id: ID joki
            limit: Jumlah data per page
            offset: Offset untuk pagination
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            
        Returns:
            GalleryResult: Gallery data
        """
        log.info(f"Get gallery by joki: joki_id={joki_id}")

        try:
            uploads = PortalJokiUploadRepository.get_by_joki(
                joki_id, limit, offset
            )

            # Filter by date if provided
            if start_date or end_date:
                filtered = []
                for upload in uploads:
                    upload_date = upload.get("tanggal")
                    if isinstance(upload_date, datetime):
                        upload_date = upload_date.date()
                    elif isinstance(upload_date, str):
                        try:
                            upload_date = datetime.fromisoformat(upload_date).date()
                        except:
                            pass
                    
                    if start_date and upload_date < start_date:
                        continue
                    if end_date and upload_date > end_date:
                        continue
                    filtered.append(upload)
                uploads = filtered

            total = len(uploads)

            # Enrich data
            for upload in uploads:
                upload["file_type"] = PortalJokiGalleryService._get_file_type(
                    upload.get("mime_type", "")
                )
                upload["file_size_formatted"] = PortalJokiGalleryService._format_file_size(
                    upload.get("file_size", 0)
                )

            log.debug(f"Gallery by joki: {len(uploads)} uploads")

            return GalleryResult.ok(
                data=uploads,
                total=total,
                limit=limit,
                offset=offset,
                filters={
                    "joki_id": joki_id,
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                },
            )

        except Exception as e:
            log.error(f"Failed to get gallery by joki: {e}")
            return GalleryResult.error(f"Gagal mengambil gallery: {str(e)}")

    @staticmethod
    def all(
        limit: Optional[int] = 100,
        offset: int = 0,
        joki_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        file_type: Optional[str] = None,
    ) -> GalleryResult:
        """
        Get all gallery uploads (admin).
        
        Args:
            limit: Jumlah data per page
            offset: Offset untuk pagination
            joki_id: Filter by joki
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            file_type: Filter by file type (image, video, pdf, etc)
            
        Returns:
            GalleryResult: Gallery data
        """
        log.info(f"Get all gallery: limit={limit}, offset={offset}")

        try:
            uploads = PortalJokiUploadRepository.get_all(
                limit=limit,
                offset=offset,
                start_date=start_date,
                end_date=end_date,
                joki_id=joki_id,
            )

            total = PortalJokiUploadRepository.get_stats(
                start_date=start_date,
                end_date=end_date,
            ).get("total_uploads", 0)

            # Filter by file type if specified
            if file_type:
                filtered = []
                for upload in uploads:
                    file_type_actual = PortalJokiGalleryService._get_file_type(
                        upload.get("mime_type", "")
                    )
                    if file_type_actual == file_type:
                        filtered.append(upload)
                uploads = filtered

            # Enrich data
            for upload in uploads:
                upload["file_type"] = PortalJokiGalleryService._get_file_type(
                    upload.get("mime_type", "")
                )
                upload["file_size_formatted"] = PortalJokiGalleryService._format_file_size(
                    upload.get("file_size", 0)
                )

            # Get stats
            stats = PortalJokiUploadRepository.get_stats(
                start_date=start_date,
                end_date=end_date,
            )

            log.debug(f"All gallery: {len(uploads)} uploads, total={total}")

            return GalleryResult.ok(
                data=uploads,
                total=total,
                limit=limit,
                offset=offset,
                filters={
                    "joki_id": joki_id,
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "file_type": file_type,
                },
                stats=stats,
            )

        except Exception as e:
            log.error(f"Failed to get all gallery: {e}")
            return GalleryResult.error(f"Gagal mengambil gallery: {str(e)}")

    @staticmethod
    def today(
        joki_id: Optional[int] = None,
    ) -> GalleryResult:
        """
        Get today's uploads.
        
        Args:
            joki_id: Filter by joki (opsional)
            
        Returns:
            GalleryResult: Today's gallery
        """
        today = date.today()
        log.info(f"Get today's gallery: joki_id={joki_id}")

        return PortalJokiGalleryService.all(
            joki_id=joki_id,
            start_date=today,
            end_date=today,
        )

    @staticmethod
    def this_week(
        joki_id: Optional[int] = None,
    ) -> GalleryResult:
        """
        Get this week's uploads.
        
        Args:
            joki_id: Filter by joki (opsional)
            
        Returns:
            GalleryResult: This week's gallery
        """
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        
        log.info(f"Get this week gallery: {start_date} - {end_date}")

        return PortalJokiGalleryService.all(
            joki_id=joki_id,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def this_month(
        joki_id: Optional[int] = None,
    ) -> GalleryResult:
        """
        Get this month's uploads.
        
        Args:
            joki_id: Filter by joki (opsional)
            
        Returns:
            GalleryResult: This month's gallery
        """
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, 28)
        
        log.info(f"Get this month gallery: {start_date} - {end_date}")

        return PortalJokiGalleryService.all(
            joki_id=joki_id,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def get_stats(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        joki_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get gallery statistics.
        
        Args:
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            joki_id: Filter by joki
            
        Returns:
            dict: Statistics
        """
        log.debug(f"Get gallery stats: start_date={start_date}, end_date={end_date}, joki_id={joki_id}")

        try:
            if joki_id:
                uploads = PortalJokiUploadRepository.get_by_joki(joki_id)
                total = len(uploads)
                total_size = sum(u.get("file_size", 0) for u in uploads)
                
                # Count by file type
                file_types = {}
                for upload in uploads:
                    file_type = PortalJokiGalleryService._get_file_type(
                        upload.get("mime_type", "")
                    )
                    file_types[file_type] = file_types.get(file_type, 0) + 1
                
                return {
                    "total_uploads": total,
                    "total_size": total_size,
                    "total_size_formatted": PortalJokiGalleryService._format_file_size(total_size),
                    "file_types": file_types,
                    "joki_id": joki_id,
                }
            else:
                stats = PortalJokiUploadRepository.get_stats(
                    start_date=start_date,
                    end_date=end_date,
                )
                
                # Add formatted size
                stats["total_size_formatted"] = PortalJokiGalleryService._format_file_size(
                    stats.get("total_size_bytes", 0)
                )
                
                return stats

        except Exception as e:
            log.error(f"Failed to get gallery stats: {e}")
            return {}

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

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
        elif mime_type.startswith("application/msword") or "word" in mime_type:
            return "document"
        elif mime_type.startswith("application/vnd.ms-excel") or "excel" in mime_type:
            return "spreadsheet"
        elif mime_type.startswith("application/zip") or "zip" in mime_type:
            return "archive"
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
gallery_service = PortalJokiGalleryService()