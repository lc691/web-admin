"""
Portal Joki - Comment Review Service

Service untuk mengupdate komentar review.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.portal_joki.repositories.review.review_repo import (
    PortalJokiReviewRepository,
)
from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class CommentResult:
    """
    Result object untuk update komentar.
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
        message: str = "Komentar berhasil diperbarui.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[list] = None,
    ) -> "CommentResult":
        """Create success result."""
        return cls(True, message, data or {}, warnings or [])
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "CommentResult":
        """Create error result."""
        return cls(False, message, data or {})


# ==========================================================
# COMMENT SERVICE
# ==========================================================
class PortalJokiCommentService:
    """
    Service Comment Review Portal Joki.
    
    Menyediakan fungsi untuk:
    - Update komentar review
    - Add komentar (via create review)
    - Get komentar history
    """

    @staticmethod
    def execute(
        *,
        review_id: int,
        komentar: str,
        updated_by: Optional[str] = None,
    ) -> CommentResult:
        """
        Update komentar review.
        
        Args:
            review_id: ID review
            komentar: Komentar baru
            updated_by: Pengupdate (opsional)
            
        Returns:
            CommentResult: Result status
        """
        log.info(f"Update comment: review_id={review_id}, updated_by={updated_by}")

        # ==========================================================
        # 1. VALIDASI REVIEW
        # ==========================================================
        try:
            review = PortalJokiReviewRepository.get(review_id)
        except Exception as e:
            log.error(f"Failed to get review: {e}")
            return CommentResult.error(f"Gagal mengambil data review: {str(e)}")

        if not review:
            log.warning(f"Review not found: ID={review_id}")
            return CommentResult.error("Review tidak ditemukan.")

        # ==========================================================
        # 2. VALIDASI KOMENTAR
        # ==========================================================
        komentar = komentar.strip() if komentar else ""

        if not komentar:
            return CommentResult.error("Komentar tidak boleh kosong.")

        if len(komentar) < 3:
            return CommentResult.error("Komentar minimal 3 karakter.")

        if len(komentar) > 2000:
            return CommentResult.error("Komentar maksimal 2000 karakter.")

        # ==========================================================
        # 3. CEK PERUBAHAN
        # ==========================================================
        old_komentar = review.get("komentar", "")
        
        if old_komentar == komentar:
            log.debug(f"No changes to comment: review_id={review_id}")
            return CommentResult.ok(
                "Tidak ada perubahan pada komentar.",
                data={
                    "review_id": review_id,
                    "komentar": komentar,
                    "unchanged": True,
                },
            )

        # ==========================================================
        # 4. UPDATE KOMENTAR
        # ==========================================================
        try:
            success = PortalJokiReviewRepository.update_comment(
                review_id,
                komentar,
            )

            if not success:
                log.error(f"Failed to update comment: review_id={review_id}")
                return CommentResult.error("Gagal memperbarui komentar.")

            log.info(f"Comment updated: review_id={review_id}")

            # Get updated review
            updated_review = PortalJokiReviewRepository.get(review_id)

            return CommentResult.ok(
                "Komentar berhasil diperbarui.",
                data={
                    "review_id": review_id,
                    "penugasan_id": review.get("penugasan_id"),
                    "old_komentar": old_komentar[:100] + "..." if len(old_komentar) > 100 else old_komentar,
                    "new_komentar": komentar,
                    "updated_by": updated_by,
                    "updated_at": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            log.error(f"Failed to update comment: {e}")
            return CommentResult.error(f"Gagal memperbarui komentar: {str(e)}")

    @staticmethod
    def add_to_review(
        *,
        penugasan_id: int,
        komentar: str,
        status: int = 1,
        reviewed_by: str = "admin",
    ) -> CommentResult:
        """
        Add comment as new review.
        
        Args:
            penugasan_id: ID penugasan
            komentar: Komentar
            status: Status review (default: 1 = upload)
            reviewed_by: Reviewer
            
        Returns:
            CommentResult: Result dengan review_id
        """
        log.info(f"Add comment to review: penugasan_id={penugasan_id}")

        # ==========================================================
        # 1. VALIDASI KOMENTAR
        # ==========================================================
        komentar = komentar.strip() if komentar else ""

        if not komentar:
            return CommentResult.error("Komentar tidak boleh kosong.")

        if len(komentar) < 3:
            return CommentResult.error("Komentar minimal 3 karakter.")

        if len(komentar) > 2000:
            return CommentResult.error("Komentar maksimal 2000 karakter.")

        # ==========================================================
        # 2. VALIDASI PENUGASAN
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return CommentResult.error(f"Gagal mengambil data penugasan: {str(e)}")

        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return CommentResult.error("Penugasan tidak ditemukan.")

        # ==========================================================
        # 3. CREATE REVIEW
        # ==========================================================
        try:
            review_id = PortalJokiReviewRepository.create(
                penugasan_id=penugasan_id,
                status=status,
                komentar=komentar,
                reviewed_by=reviewed_by,
            )

            if not review_id:
                log.error(f"Failed to create review: penugasan_id={penugasan_id}")
                return CommentResult.error("Gagal membuat review.")

            log.info(f"Review created with comment: review_id={review_id}")

            return CommentResult.ok(
                "Komentar berhasil ditambahkan.",
                data={
                    "review_id": review_id,
                    "penugasan_id": penugasan_id,
                    "status": status,
                    "komentar": komentar,
                    "reviewed_by": reviewed_by,
                },
            )

        except Exception as e:
            log.error(f"Failed to create review: {e}")
            return CommentResult.error(f"Gagal menambahkan komentar: {str(e)}")

    @staticmethod
    def get_history(
        penugasan_id: int,
    ) -> Dict[str, Any]:
        """
        Get comment history for penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: List of comments
        """
        log.debug(f"Get comment history: penugasan_id={penugasan_id}")

        try:
            reviews = PortalJokiReviewRepository.get_history(penugasan_id)

            comments = []
            for review in reviews:
                if review.get("komentar"):
                    comments.append({
                        "id": review.get("id"),
                        "komentar": review.get("komentar"),
                        "status": review.get("status"),
                        "reviewed_by": review.get("reviewed_by"),
                        "reviewed_at": review.get("reviewed_at"),
                    })

            return {
                "success": True,
                "penugasan_id": penugasan_id,
                "total": len(comments),
                "comments": comments,
            }

        except Exception as e:
            log.error(f"Failed to get comment history: {e}")
            return {
                "success": False,
                "message": f"Gagal mengambil history: {str(e)}",
                "comments": [],
                "total": 0,
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
comment_service = PortalJokiCommentService()