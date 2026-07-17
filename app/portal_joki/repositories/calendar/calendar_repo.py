"""
Portal Joki - Calendar Repository

Repository untuk mengelola data penugasan joki di calendar.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiCalendarRepository:
    """
    Repository Calendar Portal Joki.
    
    Table: portal_joki_penugasan
    """

    # ==========================================================
    # STATUS CONSTANTS
    # ==========================================================
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

    # ==========================================================
    # JOKI - MONTH
    # ==========================================================

    @staticmethod
    def get_month(
        *,
        joki_id: int,
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan ringkasan penugasan per hari untuk joki tertentu.
        
        Args:
            joki_id: ID joki
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: Data per hari dengan statistik
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    tanggal,
                    COUNT(*) AS total,
                    COUNT(DISTINCT kloter_id) AS total_kloter,
                    SUM(target_judul) AS total_target,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                GROUP BY tanggal
                ORDER BY tanggal
                """,
                (joki_id, tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Calendar month data: joki_id={joki_id}, tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    # ==========================================================
    # JOKI - DAY
    # ==========================================================

    @staticmethod
    def get_day(
        *,
        joki_id: int,
        tanggal: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan detail penugasan untuk tanggal tertentu.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal yang dicari
            
        Returns:
            List[dict]: Detail penugasan per kloter
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE
                    p.joki_id = %s
                    AND p.tanggal = %s
                ORDER BY
                    p.kloter_id,
                    p.absen_awal
                """,
                (joki_id, tanggal),
            )
            result = cur.fetchall()
            log.debug(f"Calendar day data: joki_id={joki_id}, tanggal={tanggal}, rows={len(result)}")
            return result

    # ==========================================================
    # JOKI - MONTH DETAIL
    # ==========================================================

    @staticmethod
    def get_month_detail(
        *,
        joki_id: int,
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan detail semua penugasan dalam bulan tertentu.
        
        Args:
            joki_id: ID joki
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: Detail penugasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    p.kloter_id,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    p.status,
                    p.keterangan,
                    p.created_at,
                    p.updated_at
                FROM portal_joki_penugasan p
                JOIN kloter k ON k.id = p.kloter_id
                WHERE
                    p.joki_id = %s
                    AND EXTRACT(YEAR FROM p.tanggal) = %s
                    AND EXTRACT(MONTH FROM p.tanggal) = %s
                ORDER BY
                    p.tanggal,
                    p.kloter_id,
                    p.absen_awal
                """,
                (joki_id, tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Calendar month detail: joki_id={joki_id}, tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    # ==========================================================
    # JOKI - CHECK EXISTS
    # ==========================================================

    @staticmethod
    def exists_date(
        *,
        joki_id: int,
        tanggal: date,
    ) -> bool:
        """
        Cek apakah ada penugasan untuk joki pada tanggal tertentu.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal yang dicek
            
        Returns:
            bool: True jika ada penugasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_penugasan
                WHERE joki_id = %s AND tanggal = %s
                LIMIT 1
                """,
                (joki_id, tanggal),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists date: joki_id={joki_id}, tanggal={tanggal} -> {result}")
            return result

    # ==========================================================
    # ADMIN - MONTH
    # ==========================================================

    @staticmethod
    def get_admin_month(
        *,
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan ringkasan penugasan per hari untuk semua joki (admin view).
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: Data per hari dengan statistik
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    tanggal,
                    COUNT(*) AS total,
                    COUNT(DISTINCT joki_id) AS total_joki,
                    COUNT(DISTINCT kloter_id) AS total_kloter,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai
                FROM portal_joki_penugasan
                WHERE
                    EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                GROUP BY tanggal
                ORDER BY tanggal
                """,
                (tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Admin month data: tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    # ==========================================================
    # ADMIN - DAY
    # ==========================================================

    @staticmethod
    def get_admin_day(
        *,
        tanggal: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan detail penugasan untuk tanggal tertentu (admin view).
        
        Args:
            tanggal: Tanggal yang dicari
            
        Returns:
            List[dict]: Detail penugasan per joki dan kloter
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.tanggal = %s
                ORDER BY
                    k.nama,
                    j.nama,
                    p.absen_awal
                """,
                (tanggal,),
            )
            result = cur.fetchall()
            log.debug(f"Admin day data: tanggal={tanggal}, rows={len(result)}")
            return result

    # ==========================================================
    # ADMIN - MONTH DETAIL
    # ==========================================================

    @staticmethod
    def get_admin_month_detail(
        *,
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan detail semua penugasan dalam bulan tertentu (admin view).
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: Detail penugasan semua joki
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    p.joki_id,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    p.status,
                    p.keterangan,
                    p.created_at,
                    p.updated_at
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE
                    EXTRACT(YEAR FROM p.tanggal) = %s
                    AND EXTRACT(MONTH FROM p.tanggal) = %s
                ORDER BY
                    p.tanggal,
                    k.nama,
                    j.nama,
                    p.absen_awal
                """,
                (tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Admin month detail: tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    # ==========================================================
    # ADMIN - STATISTICS
    # ==========================================================

    @staticmethod
    def get_admin_stats(
        *,
        tahun: int,
        bulan: int,
    ) -> Dict[str, Any]:
        """
        Mendapatkan statistik ringkasan untuk admin.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            dict: Statistik ringkasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_penugasan,
                    COUNT(DISTINCT joki_id) AS total_joki,
                    COUNT(DISTINCT kloter_id) AS total_kloter,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    AVG(target_judul) AS avg_target,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    ROUND(
                        COUNT(*) FILTER (WHERE status = 3) * 100.0 / NULLIF(COUNT(*), 0),
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
            log.debug(f"Admin stats: tahun={tahun}, bulan={bulan}")
            return result or {}

    # ==========================================================
    # JOKI - STATISTICS
    # ==========================================================

    @staticmethod
    def get_joki_stats(
        *,
        joki_id: int,
        tahun: int,
        bulan: int,
    ) -> Dict[str, Any]:
        """
        Mendapatkan statistik ringkasan untuk joki tertentu.
        
        Args:
            joki_id: ID joki
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            dict: Statistik ringkasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_penugasan,
                    COUNT(DISTINCT kloter_id) AS total_kloter,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    AVG(target_judul) AS avg_target,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    ROUND(
                        COUNT(*) FILTER (WHERE status = 3) * 100.0 / NULLIF(COUNT(*), 0),
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
            log.debug(f"Joki stats: joki_id={joki_id}, tahun={tahun}, bulan={bulan}")
            return result or {}

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

    @staticmethod
    def get_status_label(status: int) -> str:
        """
        Mendapatkan label status.
        
        Args:
            status: Status code
            
        Returns:
            str: Label status
        """
        return PortalJokiCalendarRepository.STATUS_LABELS.get(status, "Unknown")

    @staticmethod
    def get_status_color(status: int) -> str:
        """
        Mendapatkan warna status untuk UI.
        
        Args:
            status: Status code
            
        Returns:
            str: Warna status (Bootstrap class)
        """
        return PortalJokiCalendarRepository.STATUS_COLORS.get(status, "secondary")

    @staticmethod
    def is_completed(status: int) -> bool:
        """
        Cek apakah penugasan sudah selesai.
        
        Args:
            status: Status code
            
        Returns:
            bool: True jika selesai
        """
        return status == PortalJokiCalendarRepository.STATUS_SELESAI

    @staticmethod
    def is_pending(status: int) -> bool:
        """
        Cek apakah penugasan masih pending.
        
        Args:
            status: Status code
            
        Returns:
            bool: True jika pending
        """
        return status == PortalJokiCalendarRepository.STATUS_PENDING


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
calendar_repo = PortalJokiCalendarRepository()