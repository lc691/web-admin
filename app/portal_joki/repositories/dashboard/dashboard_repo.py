"""
Portal Joki - Dashboard Repository

Repository untuk data dashboard portal joki.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiDashboardRepository:
    """
    Repository Dashboard Portal Joki.
    
    Menyediakan data untuk dashboard joki dan admin.
    """

    # ==========================================================
    # JOKI DASHBOARD
    # ==========================================================

    @staticmethod
    def get_summary(joki_id: int) -> Dict[str, Any]:
        """
        Mendapatkan ringkasan penugasan bulan ini untuk joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Ringkasan statistik
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    COALESCE(SUM(target_judul), 0) AS total_target
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND DATE_TRUNC('month', tanggal) = DATE_TRUNC('month', CURRENT_DATE)
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Joki summary: joki_id={joki_id}")
            return result or {}

    @staticmethod
    def get_today_tasks(joki_id: int) -> List[Dict[str, Any]]:
        """
        Mendapatkan tugas hari ini untuk joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            List[dict]: List tugas hari ini
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.*,
                    k.nama AS kloter_nama,
                    j.kode AS joki_kode
                FROM portal_joki_penugasan p
                JOIN kloter k ON k.id = p.kloter_id
                JOIN joki j ON j.id = p.joki_id
                WHERE
                    p.joki_id = %s
                    AND p.tanggal = CURRENT_DATE
                ORDER BY
                    p.kloter_id,
                    p.absen_awal
                """,
                (joki_id,),
            )
            result = cur.fetchall()
            log.debug(f"Joki today tasks: joki_id={joki_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_calendar(joki_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Mendapatkan data kalender untuk 30 hari terakhir.
        
        Args:
            joki_id: ID joki
            days: Jumlah hari ke belakang
            
        Returns:
            List[dict]: Data per hari
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    tanggal,
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND tanggal >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY tanggal
                ORDER BY tanggal DESC
                """,
                (joki_id, days),
            )
            result = cur.fetchall()
            log.debug(f"Joki calendar: joki_id={joki_id}, days={days}, rows={len(result)}")
            return result

    @staticmethod
    def get_recent_uploads(joki_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan upload terbaru dari joki.
        
        Args:
            joki_id: ID joki
            limit: Jumlah data yang diambil
            
        Returns:
            List[dict]: List upload terbaru
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.*,
                    p.tanggal,
                    p.kloter_id,
                    j.kode AS joki_kode
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                WHERE p.joki_id = %s
                ORDER BY u.uploaded_at DESC
                LIMIT %s
                """,
                (joki_id, limit),
            )
            result = cur.fetchall()
            log.debug(f"Joki recent uploads: joki_id={joki_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_progress(joki_id: int) -> Dict[str, Any]:
        """
        Mendapatkan progress bulan ini untuk joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Progress dengan persentase
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    COALESCE(
                        ROUND(
                            (COUNT(*) FILTER (WHERE status = 3))::numeric
                            / NULLIF(COUNT(*), 0)
                            * 100,
                            2
                        ),
                        0
                    ) AS persen
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND DATE_TRUNC('month', tanggal) = DATE_TRUNC('month', CURRENT_DATE)
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Joki progress: joki_id={joki_id}")
            return result or {}

    @staticmethod
    def get_weekly_stats(joki_id: int) -> Dict[str, Any]:
        """
        Mendapatkan statistik minggu ini untuk joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Statistik minggu ini
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    COALESCE(SUM(target_judul), 0) AS total_target
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND DATE_TRUNC('week', tanggal) = DATE_TRUNC('week', CURRENT_DATE)
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Joki weekly stats: joki_id={joki_id}")
            return result or {}

    # ==========================================================
    # ADMIN DASHBOARD
    # ==========================================================

    @staticmethod
    def get_admin_summary() -> Dict[str, Any]:
        """
        Mendapatkan ringkasan admin untuk bulan ini.
        
        Returns:
            dict: Ringkasan statistik admin
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM joki WHERE aktif = TRUE) AS total_joki,
                    COUNT(*) AS total_penugasan,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    COALESCE(SUM(target_judul), 0) AS total_target
                FROM portal_joki_penugasan
                WHERE DATE_TRUNC('month', tanggal) = DATE_TRUNC('month', CURRENT_DATE)
                """
            )
            result = cur.fetchone()
            log.debug("Admin summary fetched")
            return result or {}

    @staticmethod
    def get_admin_today_tasks() -> List[Dict[str, Any]]:
        """
        Mendapatkan semua tugas hari ini (admin view).
        
        Returns:
            List[dict]: List semua tugas hari ini
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
                WHERE p.tanggal = CURRENT_DATE
                ORDER BY
                    k.nama,
                    j.nama,
                    p.absen_awal
                """
            )
            result = cur.fetchall()
            log.debug(f"Admin today tasks: rows={len(result)}")
            return result

    @staticmethod
    def get_admin_calendar() -> List[Dict[str, Any]]:
        """
        Mendapatkan data kalender admin untuk bulan ini.
        
        Returns:
            List[dict]: Data per hari
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    tanggal,
                    COUNT(*) AS total,
                    COUNT(DISTINCT joki_id) AS total_joki,
                    COUNT(DISTINCT kloter_id) AS total_kloter,
                    SUM(target_judul) AS total_target,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai
                FROM portal_joki_penugasan
                WHERE tanggal >= DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY tanggal
                ORDER BY tanggal
                """
            )
            result = cur.fetchall()
            log.debug(f"Admin calendar: rows={len(result)}")
            return result

    @staticmethod
    def get_admin_recent_uploads(limit: int = 20) -> List[Dict[str, Any]]:
        """
        Mendapatkan upload terbaru semua joki (admin view).
        
        Args:
            limit: Jumlah data yang diambil
            
        Returns:
            List[dict]: List upload terbaru
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.*,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                ORDER BY u.uploaded_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            result = cur.fetchall()
            log.debug(f"Admin recent uploads: rows={len(result)}")
            return result

    @staticmethod
    def get_admin_progress() -> Dict[str, Any]:
        """
        Mendapatkan progress admin untuk bulan ini.
        
        Returns:
            dict: Progress dengan persentase
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 0) AS pending,
                    COUNT(*) FILTER (WHERE status = 1) AS upload,
                    COUNT(*) FILTER (WHERE status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    COALESCE(
                        ROUND(
                            (COUNT(*) FILTER (WHERE status = 3))::numeric
                            / NULLIF(COUNT(*), 0)
                            * 100,
                            2
                        ),
                        0
                    ) AS persen
                FROM portal_joki_penugasan
                WHERE DATE_TRUNC('month', tanggal) = DATE_TRUNC('month', CURRENT_DATE)
                """
            )
            result = cur.fetchone()
            log.debug("Admin progress fetched")
            return result or {}

    @staticmethod
    def get_admin_top_joki(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan top joki berdasarkan performa bulan ini.
        
        Args:
            limit: Jumlah data yang diambil
            
        Returns:
            List[dict]: Top joki berdasarkan persentase selesai
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    j.id,
                    j.kode,
                    j.nama,
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE p.status = 3) AS selesai,
                    COUNT(*) FILTER (WHERE p.status = 2) AS revisi,
                    COALESCE(SUM(p.target_judul), 0) AS target,
                    COALESCE(
                        ROUND(
                            (COUNT(*) FILTER (WHERE p.status = 3))::numeric
                            / NULLIF(COUNT(*), 0)
                            * 100,
                            2
                        ),
                        0
                    ) AS persen
                FROM joki j
                LEFT JOIN portal_joki_penugasan p
                    ON p.joki_id = j.id
                    AND DATE_TRUNC('month', p.tanggal) = DATE_TRUNC('month', CURRENT_DATE)
                WHERE j.aktif = TRUE
                GROUP BY
                    j.id,
                    j.kode,
                    j.nama
                ORDER BY
                    persen DESC,
                    selesai DESC,
                    target DESC,
                    j.nama
                LIMIT %s
                """,
                (limit,),
            )
            result = cur.fetchall()
            log.debug(f"Admin top joki: rows={len(result)}")
            return result

    @staticmethod
    def get_admin_latest_review(limit: int = 20) -> List[Dict[str, Any]]:
        """
        Mendapatkan review terbaru (admin view).
        
        Args:
            limit: Jumlah data yang diambil
            
        Returns:
            List[dict]: List review terbaru
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    r.id,
                    r.status,
                    r.komentar,
                    r.reviewed_by,
                    r.reviewed_at,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.tanggal,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul
                FROM portal_joki_review r
                JOIN portal_joki_penugasan p ON p.id = r.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                ORDER BY r.reviewed_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            result = cur.fetchall()
            log.debug(f"Admin latest review: rows={len(result)}")
            return result

    # ==========================================================
    # ADDITIONAL STATS
    # ==========================================================

    @staticmethod
    def get_joki_performance(joki_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Mendapatkan performa joki dalam periode tertentu.
        
        Args:
            joki_id: ID joki
            days: Jumlah hari ke belakang
            
        Returns:
            dict: Statistik performa
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_tasks,
                    COUNT(*) FILTER (WHERE status = 3) AS completed,
                    COUNT(*) FILTER (WHERE status = 2) AS revision,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    COALESCE(
                        ROUND(
                            (COUNT(*) FILTER (WHERE status = 3))::numeric
                            / NULLIF(COUNT(*), 0)
                            * 100,
                            2
                        ),
                        0
                    ) AS completion_rate,
                    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) AS avg_duration_seconds
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND tanggal >= CURRENT_DATE - INTERVAL '%s days'
                """,
                (joki_id, days),
            )
            result = cur.fetchone()
            log.debug(f"Joki performance: joki_id={joki_id}, days={days}")
            return result or {}

    @staticmethod
    def get_daily_activity(joki_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """
        Mendapatkan aktivitas harian joki.
        
        Args:
            joki_id: ID joki
            days: Jumlah hari ke belakang
            
        Returns:
            List[dict]: Aktivitas per hari
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    tanggal,
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 3) AS completed,
                    COUNT(*) FILTER (WHERE status = 1) AS uploaded
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND tanggal >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY tanggal
                ORDER BY tanggal DESC
                """,
                (joki_id, days),
            )
            result = cur.fetchall()
            log.debug(f"Daily activity: joki_id={joki_id}, days={days}, rows={len(result)}")
            return result


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
dashboard_repo = PortalJokiDashboardRepository()