from typing import Optional
from functools import lru_cache

from app.core.database import get_clean_dict_cursor


class RekapDashboard:
    """
    Repository khusus Dashboard, Statistik dan Rekap.
    """

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    @staticmethod
    def get_dashboard():
        """
        Get main dashboard data.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    (
                        SELECT COUNT(*)
                        FROM joki
                        WHERE aktif = TRUE
                    ) AS total_joki,
                    (
                        SELECT COUNT(*)
                        FROM kloter
                        WHERE aktif = TRUE
                    ) AS total_kloter,
                    (
                        SELECT COUNT(*)
                        FROM catatan
                    ) AS total_transaksi,
                    (
                        SELECT COALESCE(SUM(jumlah_judul * harga_per_judul), 0)
                        FROM catatan
                    ) AS total_pendapatan
                """
            )
            return cur.fetchone()

    @staticmethod
    def get_dashboard_summary():
        """
        Get summary dashboard data.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    (
                        SELECT COUNT(*)
                        FROM joki
                        WHERE aktif = TRUE
                    ) AS total_joki,
                    (
                        SELECT COUNT(*)
                        FROM kloter
                        WHERE aktif = TRUE
                    ) AS total_kloter,
                    COUNT(*) AS total_transaksi,
                    COALESCE(SUM(jumlah_judul), 0) AS total_judul,
                    COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS total_pendapatan
                FROM catatan
                """
            )
            return cur.fetchone()

    @staticmethod
    def get_dashboard_today():
        """
        Get today's dashboard data.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS transaksi,
                    COALESCE(SUM(jumlah_judul), 0) AS judul,
                    COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS pendapatan
                FROM catatan
                WHERE tanggal = CURRENT_DATE
                """
            )
            return cur.fetchone()

    @staticmethod
    def get_dashboard_week():
        """
        Get weekly dashboard data (last 7 days).
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    tanggal,
                    COUNT(*) AS transaksi,
                    COALESCE(SUM(jumlah_judul), 0) AS judul,
                    COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS pendapatan
                FROM catatan
                WHERE tanggal >= CURRENT_DATE - INTERVAL '6 day'
                GROUP BY tanggal
                ORDER BY tanggal
                """
            )
            return cur.fetchall()

    @staticmethod
    def get_dashboard_top_joki():
        """
        Get top 5 joki for today.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    j.id,
                    j.kode,
                    j.nama,
                    SUM(c.jumlah_judul) AS jumlah_judul,
                    SUM(c.jumlah_judul * c.harga_per_judul) AS total_pendapatan
                FROM catatan c
                JOIN joki j ON j.id = c.joki_id
                WHERE c.tanggal = CURRENT_DATE
                GROUP BY j.id, j.kode, j.nama
                ORDER BY total_pendapatan DESC
                LIMIT 5
                """
            )
            return cur.fetchall()

    @staticmethod
    def get_dashboard_top_kloter():
        """
        Get top 5 kloter for today.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    k.id,
                    k.kode,
                    k.nama,
                    SUM(c.jumlah_judul) AS jumlah_judul,
                    SUM(c.jumlah_judul * c.harga_per_judul) AS total_pendapatan
                FROM catatan c
                JOIN kloter k ON k.id = c.kloter_id
                WHERE c.tanggal = CURRENT_DATE
                GROUP BY k.id, k.kode, k.nama
                ORDER BY total_pendapatan DESC
                LIMIT 5
                """
            )
            return cur.fetchall()

    # ==========================================================
    # ADDITIONAL METHODS
    # ==========================================================

    @staticmethod
    def get_dashboard_by_date_range(
        start_date: str,
        end_date: str,
    ) -> dict:
        """
        Get dashboard data for date range.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_transaksi,
                    COALESCE(SUM(jumlah_judul), 0) AS total_judul,
                    COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS total_pendapatan,
                    COUNT(DISTINCT joki_id) AS total_joki,
                    COUNT(DISTINCT kloter_id) AS total_kloter
                FROM catatan
                WHERE tanggal BETWEEN %s AND %s
                """,
                (start_date, end_date),
            )
            return cur.fetchone()

    @staticmethod
    def get_dashboard_monthly(year: int) -> list[dict]:
        """
        Get monthly dashboard data for chart.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    EXTRACT(MONTH FROM tanggal) AS month,
                    COUNT(*) AS transaksi,
                    COALESCE(SUM(jumlah_judul), 0) AS judul,
                    COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS pendapatan
                FROM catatan
                WHERE EXTRACT(YEAR FROM tanggal) = %s
                GROUP BY EXTRACT(MONTH FROM tanggal)
                ORDER BY month
                """,
                (year,),
            )
            return cur.fetchall()

    @staticmethod
    def get_dashboard_export(start_date: str, end_date: str) -> list[dict]:
        """
        Get detailed data for export.
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.tanggal,
                    c.jumlah_judul,
                    c.harga_per_judul,
                    c.jumlah_judul * c.harga_per_judul AS total,
                    j.kode AS joki_kode,
                    j.nama AS joki_nama,
                    k.kode AS kloter_kode,
                    k.nama AS kloter_nama
                FROM catatan c
                LEFT JOIN joki j ON j.id = c.joki_id
                LEFT JOIN kloter k ON k.id = c.kloter_id
                WHERE c.tanggal BETWEEN %s AND %s
                ORDER BY c.tanggal DESC
                """,
                (start_date, end_date),
            )
            return cur.fetchall()