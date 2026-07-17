"""
Portal Joki - Laporan Repository

Repository untuk data laporan dan statistik portal joki.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiLaporanRepository:
    """
    Repository Laporan Portal Joki.
    
    Menyediakan data untuk laporan harian, bulanan, dan statistik.
    """

    # ==========================================================
    # HARIAN (Daily Report)
    # ==========================================================

    @staticmethod
    def get_harian(
        tanggal: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan laporan harian untuk tanggal tertentu.
        
        Args:
            tanggal: Tanggal laporan
            
        Returns:
            List[dict]: Detail penugasan per joki dan kloter
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    p.status,
                    u.file_path,
                    r.komentar
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                LEFT JOIN LATERAL (
                    SELECT file_path
                    FROM portal_joki_upload
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) u ON TRUE
                LEFT JOIN LATERAL (
                    SELECT komentar
                    FROM portal_joki_review
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) r ON TRUE
                WHERE p.tanggal = %s
                ORDER BY
                    j.nama,
                    k.nama,
                    p.absen_awal
                """,
                (tanggal,),
            )
            result = cur.fetchall()
            log.debug(f"Laporan harian: tanggal={tanggal}, rows={len(result)}")
            return result

    @staticmethod
    def get_harian_by_joki(
        tanggal: date,
        joki_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan laporan harian untuk joki tertentu.
        
        Args:
            tanggal: Tanggal laporan
            joki_id: ID joki
            
        Returns:
            List[dict]: Detail penugasan joki pada tanggal tersebut
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    p.status,
                    u.file_path,
                    r.komentar
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                LEFT JOIN LATERAL (
                    SELECT file_path
                    FROM portal_joki_upload
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) u ON TRUE
                LEFT JOIN LATERAL (
                    SELECT komentar
                    FROM portal_joki_review
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) r ON TRUE
                WHERE p.tanggal = %s AND p.joki_id = %s
                ORDER BY
                    k.nama,
                    p.absen_awal
                """,
                (tanggal, joki_id),
            )
            result = cur.fetchall()
            log.debug(f"Laporan harian by joki: tanggal={tanggal}, joki_id={joki_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_harian_by_kloter(
        tanggal: date,
        kloter_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan laporan harian untuk kloter tertentu.
        
        Args:
            tanggal: Tanggal laporan
            kloter_id: ID kloter
            
        Returns:
            List[dict]: Detail penugasan kloter pada tanggal tersebut
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    p.status,
                    u.file_path,
                    r.komentar
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                LEFT JOIN LATERAL (
                    SELECT file_path
                    FROM portal_joki_upload
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) u ON TRUE
                LEFT JOIN LATERAL (
                    SELECT komentar
                    FROM portal_joki_review
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) r ON TRUE
                WHERE p.tanggal = %s AND p.kloter_id = %s
                ORDER BY
                    j.nama,
                    p.absen_awal
                """,
                (tanggal, kloter_id),
            )
            result = cur.fetchall()
            log.debug(f"Laporan harian by kloter: tanggal={tanggal}, kloter_id={kloter_id}, rows={len(result)}")
            return result

    # ==========================================================
    # BULANAN (Monthly Report)
    # ==========================================================

    @staticmethod
    def get_bulanan(
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan laporan bulanan per joki.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: Ringkasan performa per joki
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    j.id,
                    j.nama,
                    j.kode,
                    COUNT(*) AS total_penugasan,
                    COALESCE(SUM(p.target_judul), 0) AS total_target,
                    COUNT(*) FILTER (WHERE p.status = 0) AS pending,
                    COUNT(*) FILTER (WHERE p.status = 1) AS upload,
                    COUNT(*) FILTER (WHERE p.status = 2) AS revisi,
                    COUNT(*) FILTER (WHERE p.status = 3) AS selesai,
                    ROUND(
                        (COUNT(*) FILTER (WHERE p.status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                WHERE
                    EXTRACT(YEAR FROM p.tanggal) = %s
                    AND EXTRACT(MONTH FROM p.tanggal) = %s
                GROUP BY
                    j.id,
                    j.nama,
                    j.kode
                ORDER BY
                    j.nama
                """,
                (tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Laporan bulanan: tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    @staticmethod
    def get_bulanan_detail(
        tahun: int,
        bulan: int,
        joki_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan laporan bulanan detail per hari.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            joki_id: ID joki (opsional)
            
        Returns:
            List[dict]: Detail penugasan per hari
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    p.status
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE
                    EXTRACT(YEAR FROM p.tanggal) = %s
                    AND EXTRACT(MONTH FROM p.tanggal) = %s
            """
            params = [tahun, bulan]
            
            if joki_id is not None:
                query += " AND p.joki_id = %s"
                params.append(joki_id)
            
            query += """
                ORDER BY
                    p.tanggal,
                    j.nama,
                    k.nama,
                    p.absen_awal
            """
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Laporan bulanan detail: tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    # ==========================================================
    # STATISTIK (Statistics)
    # ==========================================================

    @staticmethod
    def get_statistik() -> Dict[str, Any]:
        """
        Mendapatkan statistik keseluruhan.
        
        Returns:
            dict: Statistik total
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
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan
                """
            )
            result = cur.fetchone()
            log.debug("Statistik keseluruhan fetched")
            return result or {}

    @staticmethod
    def get_statistik_period(
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Mendapatkan statistik dalam periode tertentu.
        
        Args:
            start_date: Tanggal awal
            end_date: Tanggal akhir
            
        Returns:
            dict: Statistik dalam periode
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
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan
                WHERE tanggal BETWEEN %s AND %s
                """,
                (start_date, end_date),
            )
            result = cur.fetchone()
            log.debug(f"Statistik period: {start_date} - {end_date}")
            return result or {}

    @staticmethod
    def get_statistik_by_joki(
        joki_id: int,
    ) -> Dict[str, Any]:
        """
        Mendapatkan statistik untuk joki tertentu.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Statistik joki
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
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate,
                    COUNT(DISTINCT kloter_id) AS total_kloter
                FROM portal_joki_penugasan
                WHERE joki_id = %s
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Statistik by joki: joki_id={joki_id}")
            return result or {}

    # ==========================================================
    # REKAP (Summary)
    # ==========================================================

    @staticmethod
    def get_rekap_harian(
        tanggal: date,
    ) -> Dict[str, Any]:
        """
        Mendapatkan rekap harian.
        
        Args:
            tanggal: Tanggal rekap
            
        Returns:
            dict: Rekap statistik harian
        """
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
                    COALESCE(SUM(target_judul), 0) AS total_target
                FROM portal_joki_penugasan
                WHERE tanggal = %s
                """,
                (tanggal,),
            )
            result = cur.fetchone()
            log.debug(f"Rekap harian: tanggal={tanggal}")
            return result or {}

    @staticmethod
    def get_rekap_bulanan(
        tahun: int,
        bulan: int,
    ) -> Dict[str, Any]:
        """
        Mendapatkan rekap bulanan.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            dict: Rekap statistik bulanan
        """
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
            log.debug(f"Rekap bulanan: tahun={tahun}, bulan={bulan}")
            return result or {}

    # ==========================================================
    # EKSPOR (Export)
    # ==========================================================

    @staticmethod
    def get_for_export(
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan data untuk ekspor dalam rentang tanggal.
        
        Args:
            start_date: Tanggal awal
            end_date: Tanggal akhir
            
        Returns:
            List[dict]: Data lengkap untuk ekspor
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    CASE p.status
                        WHEN 0 THEN 'Pending'
                        WHEN 1 THEN 'Upload'
                        WHEN 2 THEN 'Revisi'
                        WHEN 3 THEN 'Selesai'
                    END AS status_label,
                    u.file_path,
                    r.komentar
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                LEFT JOIN LATERAL (
                    SELECT file_path
                    FROM portal_joki_upload
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) u ON TRUE
                LEFT JOIN LATERAL (
                    SELECT komentar
                    FROM portal_joki_review
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) r ON TRUE
                WHERE p.tanggal BETWEEN %s AND %s
                ORDER BY
                    p.tanggal,
                    j.nama,
                    k.nama,
                    p.absen_awal
                """,
                (start_date, end_date),
            )
            result = cur.fetchall()
            log.debug(f"Export data: {start_date} - {end_date}, rows={len(result)}")
            return result

    # ==========================================================
    # PERFORMANCE TREND
    # ==========================================================

    @staticmethod
    def get_performance_trend(
        joki_id: int,
        months: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan trend performa joki per bulan.
        
        Args:
            joki_id: ID joki
            months: Jumlah bulan ke belakang
            
        Returns:
            List[dict]: Trend performa per bulan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    DATE_TRUNC('month', tanggal) AS bulan,
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 3) AS selesai,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND tanggal >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '%s months'
                GROUP BY DATE_TRUNC('month', tanggal)
                ORDER BY bulan DESC
                """,
                (joki_id, months),
            )
            result = cur.fetchall()
            log.debug(f"Performance trend: joki_id={joki_id}, months={months}, rows={len(result)}")
            return result


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
laporan_repo = PortalJokiLaporanRepository()