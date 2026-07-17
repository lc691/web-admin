"""
Portal Joki - Review Repository

Repository untuk mengelola data review penugasan joki.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiReviewRepository:
    """
    Repository Review Portal Joki.
    
    Table: portal_joki_review
    """

    # ==========================================================
    # STATUS CONSTANTS
    # ==========================================================
    STATUS_APPROVED = 1
    STATUS_REVISION = 2
    STATUS_REJECTED = 3
    
    STATUS_LABELS = {
        1: "Approved",
        2: "Revision",
        3: "Rejected",
    }
    
    STATUS_COLORS = {
        1: "success",
        2: "warning",
        3: "danger",
    }

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        penugasan_id: int,
        status: int,
        komentar: Optional[str] = None,
        reviewed_by: str = "admin",
    ) -> Optional[int]:
        """
        Membuat review baru.
        
        Args:
            penugasan_id: ID penugasan
            status: Status review (1=Approved, 2=Revision, 3=Rejected)
            komentar: Komentar review (opsional)
            reviewed_by: Nama/ID reviewer
            
        Returns:
            int: ID review baru atau None jika gagal
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    INSERT INTO portal_joki_review (
                        penugasan_id,
                        status,
                        komentar,
                        reviewed_by,
                        reviewed_at,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                    """,
                    (penugasan_id, status, komentar, reviewed_by),
                )
                result = cur.fetchone()
                review_id = result["id"] if result else None
                log.info(f"Created review: ID={review_id}, penugasan_id={penugasan_id}, status={status}")
                return review_id
        except Exception as e:
            log.error(f"Failed to create review: {e}")
            return None

    @staticmethod
    def create_approved(
        penugasan_id: int,
        komentar: Optional[str] = None,
        reviewed_by: str = "admin",
    ) -> Optional[int]:
        """
        Membuat review dengan status Approved.
        
        Args:
            penugasan_id: ID penugasan
            komentar: Komentar (opsional)
            reviewed_by: Nama/ID reviewer
            
        Returns:
            int: ID review baru atau None
        """
        return PortalJokiReviewRepository.create(
            penugasan_id,
            PortalJokiReviewRepository.STATUS_APPROVED,
            komentar,
            reviewed_by,
        )

    @staticmethod
    def create_revision(
        penugasan_id: int,
        komentar: str,
        reviewed_by: str = "admin",
    ) -> Optional[int]:
        """
        Membuat review dengan status Revision.
        
        Args:
            penugasan_id: ID penugasan
            komentar: Komentar revisi (wajib)
            reviewed_by: Nama/ID reviewer
            
        Returns:
            int: ID review baru atau None
        """
        return PortalJokiReviewRepository.create(
            penugasan_id,
            PortalJokiReviewRepository.STATUS_REVISION,
            komentar,
            reviewed_by,
        )

    @staticmethod
    def create_rejected(
        penugasan_id: int,
        komentar: str,
        reviewed_by: str = "admin",
    ) -> Optional[int]:
        """
        Membuat review dengan status Rejected.
        
        Args:
            penugasan_id: ID penugasan
            komentar: Komentar reject (wajib)
            reviewed_by: Nama/ID reviewer
            
        Returns:
            int: ID review baru atau None
        """
        return PortalJokiReviewRepository.create(
            penugasan_id,
            PortalJokiReviewRepository.STATUS_REJECTED,
            komentar,
            reviewed_by,
        )

    # ==========================================================
    # DETAIL / GET
    # ==========================================================

    @staticmethod
    def get(review_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan detail review berdasarkan ID.
        
        Args:
            review_id: ID review
            
        Returns:
            dict: Detail review atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    r.*,
                    p.tanggal,
                    p.kloter_id,
                    j.id AS joki_id,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode
                FROM portal_joki_review r
                JOIN portal_joki_penugasan p ON p.id = r.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                WHERE r.id = %s
                LIMIT 1
                """,
                (review_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get review: review_id={review_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_penugasan(penugasan_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan review terbaru untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Review terbaru atau None
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM portal_joki_review
                WHERE penugasan_id = %s
                ORDER BY reviewed_at DESC, id DESC
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get by penugasan: penugasan_id={penugasan_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_last(penugasan_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan review terakhir untuk penugasan (alias get_by_penugasan).
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Review terakhir atau None
        """
        return PortalJokiReviewRepository.get_by_penugasan(penugasan_id)

    @staticmethod
    def get_history(penugasan_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Mendapatkan history review untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            limit: Jumlah data yang diambil
            
        Returns:
            List[dict]: History review
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT *
                FROM portal_joki_review
                WHERE penugasan_id = %s
                ORDER BY reviewed_at DESC, id DESC
            """
            params = [penugasan_id]
            
            if limit is not None:
                query += " LIMIT %s"
                params.append(limit)
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get history: penugasan_id={penugasan_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_history_with_detail(penugasan_id: int) -> List[Dict[str, Any]]:
        """
        Mendapatkan history review dengan detail penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            List[dict]: History review dengan detail
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    r.*,
                    p.tanggal,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode
                FROM portal_joki_review r
                JOIN portal_joki_penugasan p ON p.id = r.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                WHERE r.penugasan_id = %s
                ORDER BY r.reviewed_at DESC, r.id DESC
                """,
                (penugasan_id,),
            )
            result = cur.fetchall()
            log.debug(f"Get history with detail: penugasan_id={penugasan_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_by_status(
        status: int,
        limit: Optional[int] = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan review berdasarkan status.
        
        Args:
            status: Status review
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            List[dict]: List review
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    r.*,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode
                FROM portal_joki_review r
                JOIN portal_joki_penugasan p ON p.id = r.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                WHERE r.status = %s
                ORDER BY r.reviewed_at DESC
                LIMIT %s OFFSET %s
            """
            cur.execute(query, (status, limit, offset))
            result = cur.fetchall()
            log.debug(f"Get by status: status={status}, rows={len(result)}")
            return result

    @staticmethod
    def get_pending_reviews(limit: int = 50) -> List[Dict[str, Any]]:
        """
        Mendapatkan review yang perlu ditindaklanjuti.
        
        Args:
            limit: Jumlah data yang diambil
            
        Returns:
            List[dict]: List review pending
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    r.*,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode
                FROM portal_joki_review r
                JOIN portal_joki_penugasan p ON p.id = r.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                WHERE r.status = 2 OR r.status = 3
                ORDER BY r.reviewed_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            result = cur.fetchall()
            log.debug(f"Get pending reviews: rows={len(result)}")
            return result

    # ==========================================================
    # UPDATE
    # ==========================================================

    @staticmethod
    def update_comment(
        review_id: int,
        komentar: str,
    ) -> bool:
        """
        Update komentar review.
        
        Args:
            review_id: ID review
            komentar: Komentar baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE portal_joki_review
                    SET
                        komentar = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (komentar, review_id),
                )
                affected = cur.rowcount
                log.info(f"Updated comment: review_id={review_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update comment for review_id {review_id}: {e}")
            return False

    @staticmethod
    def update_status(
        review_id: int,
        status: int,
    ) -> bool:
        """
        Update status review.
        
        Args:
            review_id: ID review
            status: Status baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE portal_joki_review
                    SET
                        status = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (status, review_id),
                )
                affected = cur.rowcount
                log.info(f"Updated status: review_id={review_id}, status={status}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update status for review_id {review_id}: {e}")
            return False

    @staticmethod
    def update(
        review_id: int,
        status: int,
        komentar: Optional[str] = None,
    ) -> bool:
        """
        Update review (status dan komentar).
        
        Args:
            review_id: ID review
            status: Status baru
            komentar: Komentar baru (opsional)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                if komentar is not None:
                    cur.execute(
                        """
                        UPDATE portal_joki_review
                        SET
                            status = %s,
                            komentar = %s,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (status, komentar, review_id),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE portal_joki_review
                        SET
                            status = %s,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (status, review_id),
                    )
                affected = cur.rowcount
                log.info(f"Updated review: review_id={review_id}, status={status}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update review_id {review_id}: {e}")
            return False

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(review_id: int) -> bool:
        """
        Menghapus review.
        
        Args:
            review_id: ID review
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_review
                    WHERE id = %s
                    """,
                    (review_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted review: review_id={review_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to delete review_id {review_id}: {e}")
            return False

    @staticmethod
    def delete_by_penugasan(penugasan_id: int) -> int:
        """
        Menghapus semua review untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            int: Jumlah review yang dihapus
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_review
                    WHERE penugasan_id = %s
                    """,
                    (penugasan_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted reviews by penugasan: penugasan_id={penugasan_id}, affected={affected}")
                return affected
        except Exception as e:
            log.error(f"Failed to delete reviews for penugasan_id {penugasan_id}: {e}")
            return 0

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists(review_id: int) -> bool:
        """
        Cek apakah review ada.
        
        Args:
            review_id: ID review
            
        Returns:
            bool: True jika ada
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_review
                WHERE id = %s
                """,
                (review_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists: review_id={review_id} -> {result}")
            return result

    @staticmethod
    def has_review(penugasan_id: int) -> bool:
        """
        Cek apakah penugasan sudah memiliki review.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            bool: True jika ada review
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_review
                WHERE penugasan_id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check has review: penugasan_id={penugasan_id} -> {result}")
            return result

    @staticmethod
    def has_pending_review(penugasan_id: int) -> bool:
        """
        Cek apakah penugasan memiliki review pending (revisi/reject).
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            bool: True jika ada review pending
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_review
                WHERE penugasan_id = %s
                  AND status IN (%s, %s)
                LIMIT 1
                """,
                (penugasan_id, 
                 PortalJokiReviewRepository.STATUS_REVISION,
                 PortalJokiReviewRepository.STATUS_REJECTED),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check has pending review: penugasan_id={penugasan_id} -> {result}")
            return result

    # ==========================================================
    # COUNT
    # ==========================================================

    @staticmethod
    def count(
        status: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """
        Menghitung total review dengan filter.
        
        Args:
            status: Filter by status
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            
        Returns:
            int: Total count
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT COUNT(*) AS total
                FROM portal_joki_review r
                JOIN portal_joki_penugasan p ON p.id = r.penugasan_id
                WHERE 1=1
            """
            params = []
            
            if status is not None:
                query += " AND r.status = %s"
                params.append(status)
            
            if start_date is not None:
                query += " AND p.tanggal >= %s"
                params.append(start_date)
            
            if end_date is not None:
                query += " AND p.tanggal <= %s"
                params.append(end_date)
            
            cur.execute(query, tuple(params))
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count reviews: {total}")
            return total

    @staticmethod
    def count_by_penugasan(penugasan_id: int) -> int:
        """
        Menghitung total review untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            int: Total review
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM portal_joki_review
                WHERE penugasan_id = %s
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count reviews by penugasan: penugasan_id={penugasan_id}, total={total}")
            return total

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

    @staticmethod
    def get_status_label(status: int) -> str:
        """Mendapatkan label status."""
        return PortalJokiReviewRepository.STATUS_LABELS.get(status, "Unknown")

    @staticmethod
    def get_status_color(status: int) -> str:
        """Mendapatkan warna status untuk UI."""
        return PortalJokiReviewRepository.STATUS_COLORS.get(status, "secondary")

    @staticmethod
    def is_approved(status: int) -> bool:
        """Cek apakah status Approved."""
        return status == PortalJokiReviewRepository.STATUS_APPROVED

    @staticmethod
    def is_revision(status: int) -> bool:
        """Cek apakah status Revision."""
        return status == PortalJokiReviewRepository.STATUS_REVISION

    @staticmethod
    def is_rejected(status: int) -> bool:
        """Cek apakah status Rejected."""
        return status == PortalJokiReviewRepository.STATUS_REJECTED


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
review_repo = PortalJokiReviewRepository()