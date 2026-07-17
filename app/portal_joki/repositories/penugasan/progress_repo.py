"""
Portal Joki - Progress Repository

Repository untuk tracking progress penugasan joki.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiProgressRepository:
    """
    Repository Progress Portal Joki.
    
    Menyediakan data progress untuk penugasan termasuk upload, review, dan statistik.
    """

    # ==========================================================
    # STATUS CONSTANTS
    # ==========================================================
    STATUS_PENDING = 0
    STATUS_UPLOAD = 1
    STATUS_REVISI = 2
    STATUS_SELESAI = 3

    # ==========================================================
    # DETAIL PENUGASAN
    # ==========================================================

    @staticmethod
    def get(penugasan_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan detail penugasan untuk progress tracking.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Detail penugasan atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    p.status,
                    p.target_judul,
                    p.absen_awal,
                    p.absen_akhir,
                    p.instruksi,
                    p.deadline,
                    p.created_at,
                    p.updated_at,
                    j.id AS joki_id,
                    j.kode AS joki_kode,
                    j.nama AS joki_nama,
                    k.id AS kloter_id,
                    k.nama AS kloter_nama
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get progress detail: penugasan_id={penugasan_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_joki_date(
        joki_id: int,
        tanggal: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan progress penugasan joki pada tanggal tertentu.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal penugasan
            
        Returns:
            List[dict]: List penugasan dengan progress
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    p.status,
                    p.target_judul,
                    p.absen_awal,
                    p.absen_akhir,
                    k.nama AS kloter_nama,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_upload u
                        WHERE u.penugasan_id = p.id
                    ) AS total_upload,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_review
                FROM portal_joki_penugasan p
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.joki_id = %s AND p.tanggal = %s
                ORDER BY p.kloter_id, p.absen_awal
                """,
                (joki_id, tanggal),
            )
            result = cur.fetchall()
            log.debug(f"Get by joki date: joki_id={joki_id}, tanggal={tanggal}, rows={len(result)}")
            return result

    @staticmethod
    def get_by_kloter_date(
        kloter_id: int,
        tanggal: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan progress penugasan kloter pada tanggal tertentu.
        
        Args:
            kloter_id: ID kloter
            tanggal: Tanggal penugasan
            
        Returns:
            List[dict]: List penugasan dengan progress
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    p.status,
                    p.target_judul,
                    p.absen_awal,
                    p.absen_akhir,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_upload u
                        WHERE u.penugasan_id = p.id
                    ) AS total_upload,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_review
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                WHERE p.kloter_id = %s AND p.tanggal = %s
                ORDER BY j.nama, p.absen_awal
                """,
                (kloter_id, tanggal),
            )
            result = cur.fetchall()
            log.debug(f"Get by kloter date: kloter_id={kloter_id}, tanggal={tanggal}, rows={len(result)}")
            return result

    # ==========================================================
    # UPLOADS
    # ==========================================================

    @staticmethod
    def get_uploads(penugasan_id: int) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua upload untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            List[dict]: List upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nomor,
                    file_path,
                    original_filename,
                    mime_type,
                    file_size,
                    catatan,
                    uploaded_at
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                ORDER BY nomor, uploaded_at
                """,
                (penugasan_id,),
            )
            result = cur.fetchall()
            log.debug(f"Get uploads: penugasan_id={penugasan_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_latest_upload(penugasan_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan upload terbaru untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Upload terbaru atau None
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nomor,
                    file_path,
                    original_filename,
                    mime_type,
                    file_size,
                    catatan,
                    uploaded_at
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                ORDER BY uploaded_at DESC, id DESC
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get latest upload: penugasan_id={penugasan_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_upload_count(penugasan_id: int) -> int:
        """
        Mendapatkan jumlah upload untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            int: Jumlah upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Get upload count: penugasan_id={penugasan_id}, total={total}")
            return total

    # ==========================================================
    # REVIEWS
    # ==========================================================

    @staticmethod
    def get_reviews(penugasan_id: int) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua review untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            List[dict]: List review
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    status,
                    komentar,
                    reviewed_by,
                    reviewed_at
                FROM portal_joki_review
                WHERE penugasan_id = %s
                ORDER BY reviewed_at DESC, id DESC
                """,
                (penugasan_id,),
            )
            result = cur.fetchall()
            log.debug(f"Get reviews: penugasan_id={penugasan_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_latest_review(penugasan_id: int) -> Optional[Dict[str, Any]]:
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
                SELECT
                    id,
                    status,
                    komentar,
                    reviewed_by,
                    reviewed_at
                FROM portal_joki_review
                WHERE penugasan_id = %s
                ORDER BY reviewed_at DESC, id DESC
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get latest review: penugasan_id={penugasan_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_review_count(penugasan_id: int) -> int:
        """
        Mendapatkan jumlah review untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            int: Jumlah review
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
            log.debug(f"Get review count: penugasan_id={penugasan_id}, total={total}")
            return total

    # ==========================================================
    # COUNTER / STATISTICS
    # ==========================================================

    @staticmethod
    def get_counter(penugasan_id: int) -> Dict[str, Any]:
        """
        Mendapatkan counter status review.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Counter upload, revisi, approve
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS approve
                FROM portal_joki_review
                WHERE penugasan_id = %s
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get counter: penugasan_id={penugasan_id}")
            return result or {}

    @staticmethod
    def get_progress_stats(penugasan_id: int) -> Dict[str, Any]:
        """
        Mendapatkan statistik progress lengkap.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Statistik progress
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.status AS current_status,
                    p.target_judul,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_upload u
                        WHERE u.penugasan_id = p.id
                    ) AS total_upload,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_review,
                    (
                        SELECT COUNT(*) FILTER (WHERE status = 1)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_approved,
                    (
                        SELECT COUNT(*) FILTER (WHERE status = 2)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_revision,
                    (
                        SELECT COUNT(*) FILTER (WHERE status = 3)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_rejected
                FROM portal_joki_penugasan p
                WHERE p.id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get progress stats: penugasan_id={penugasan_id}")
            return result or {}

    # ==========================================================
    # BULK PROGRESS
    # ==========================================================

    @staticmethod
    def get_bulk_progress(
        penugasan_ids: List[int],
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan progress untuk multiple penugasan.
        
        Args:
            penugasan_ids: List ID penugasan
            
        Returns:
            List[dict]: List progress
        """
        if not penugasan_ids:
            return []
        
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    p.status,
                    p.target_judul,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_upload u
                        WHERE u.penugasan_id = p.id
                    ) AS total_upload,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_review
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.id = ANY(%s)
                ORDER BY p.tanggal DESC, j.nama
                """,
                (penugasan_ids,),
            )
            result = cur.fetchall()
            log.debug(f"Get bulk progress: {len(penugasan_ids)} ids, rows={len(result)}")
            return result

    # ==========================================================
    # PROGRESS BY PERIOD
    # ==========================================================

    @staticmethod
    def get_progress_by_period(
        start_date: date,
        end_date: date,
        joki_id: Optional[int] = None,
        kloter_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan progress dalam periode tertentu.
        
        Args:
            start_date: Tanggal awal
            end_date: Tanggal akhir
            joki_id: Filter by joki (opsional)
            kloter_id: Filter by kloter (opsional)
            
        Returns:
            List[dict]: List progress
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    p.id,
                    p.tanggal,
                    p.status,
                    p.target_judul,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_upload u
                        WHERE u.penugasan_id = p.id
                    ) AS total_upload,
                    (
                        SELECT COUNT(*)
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS total_review
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.tanggal BETWEEN %s AND %s
            """
            params = [start_date, end_date]
            
            if joki_id is not None:
                query += " AND p.joki_id = %s"
                params.append(joki_id)
            
            if kloter_id is not None:
                query += " AND p.kloter_id = %s"
                params.append(kloter_id)
            
            query += " ORDER BY p.tanggal DESC, j.nama"
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get progress by period: {start_date} - {end_date}, rows={len(result)}")
            return result

    # ==========================================================
    # PROGRESS SUMMARY
    # ==========================================================

    @staticmethod
    def get_summary(
        joki_id: int,
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan summary progress untuk joki.
        
        Args:
            joki_id: ID joki
            bulan: Bulan (opsional, default: bulan ini)
            tahun: Tahun (opsional, default: tahun ini)
            
        Returns:
            dict: Summary progress
        """
        if bulan is None:
            bulan = datetime.now().month
        if tahun is None:
            tahun = datetime.now().year
        
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                """,
                (joki_id, tahun, bulan),
            )
            result = cur.fetchone()
            log.debug(f"Get summary: joki_id={joki_id}, bulan={bulan}, tahun={tahun}")
            return result or {}

    @staticmethod
    def get_admin_summary(
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan summary progress admin untuk semua joki.
        
        Args:
            bulan: Bulan (opsional, default: bulan ini)
            tahun: Tahun (opsional, default: tahun ini)
            
        Returns:
            dict: Summary progress admin
        """
        if bulan is None:
            bulan = datetime.now().month
        if tahun is None:
            tahun = datetime.now().year
        
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(DISTINCT joki_id) AS total_joki,
                    COUNT(DISTINCT kloter_id) AS total_kloter,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan
                WHERE
                    EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                """,
                (tahun, bulan),
            )
            result = cur.fetchone()
            log.debug(f"Get admin summary: bulan={bulan}, tahun={tahun}")
            return result or {}

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists(penugasan_id: int) -> bool:
        """
        Cek apakah penugasan ada.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            bool: True jika ada
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_penugasan
                WHERE id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists: penugasan_id={penugasan_id} -> {result}")
            return result

    @staticmethod
    def has_upload(penugasan_id: int) -> bool:
        """
        Cek apakah penugasan sudah memiliki upload.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            bool: True jika ada upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check has upload: penugasan_id={penugasan_id} -> {result}")
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


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
progress_repo = PortalJokiProgressRepository()