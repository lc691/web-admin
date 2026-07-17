from typing import Optional

from app.core.database import get_clean_dict_cursor


class RekapRepository:
    """
    Repository untuk seluruh laporan.

    Mendukung:
    - Dashboard
    - Harian
    - Bulanan
    - Tahunan
    - Rekap Joki
    - Rekap Kloter
    - Detail Joki
    - Detail Kloter
    - Export
    - Trend
    """

    # ==========================================================
    # PRIVATE HELPERS
    # ==========================================================

    @staticmethod
    def _validate_period(periode: str) -> str:
        """Validate periode parameter."""
        valid_periods = ["harian", "bulanan", "tahunan"]
        if periode not in valid_periods:
            raise ValueError(f"Periode harus salah satu dari: {', '.join(valid_periods)}")
        return periode

    @staticmethod
    def _build_filter(
        periode: str = "harian",
        tanggal: Optional[str] = None,
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
        alias: str = "c",
    ):
        """
        Membuat SQL filter berdasarkan periode.

        Return
        ------
        where_sql : str
        params    : list
        """
        periode = RekapRepository._validate_period(periode)
        
        where = []
        params = []

        if periode == "harian":
            if tanggal:
                where.append(f"{alias}.tanggal = %s")
                params.append(tanggal)

        elif periode == "bulanan":
            if tahun:
                where.append(f"EXTRACT(YEAR FROM {alias}.tanggal) = %s")
                params.append(tahun)
            if bulan:
                where.append(f"EXTRACT(MONTH FROM {alias}.tanggal) = %s")
                params.append(bulan)

        elif periode == "tahunan":
            if tahun:
                where.append(f"EXTRACT(YEAR FROM {alias}.tanggal) = %s")
                params.append(tahun)

        if where:
            return "WHERE " + " AND ".join(where), params

        return "", params

    # ==========================================================
    # TODAY
    # ==========================================================

    @staticmethod
    def get_today():
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

    # ==========================================================
    # SUMMARY
    # ==========================================================

    @staticmethod
    def _get_total(
        periode: str,
        tanggal: Optional[str] = None,
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
    ):
        """
        Summary laporan berdasarkan periode.
        """
        where_sql, params = RekapRepository._build_filter(
            periode=periode,
            tanggal=tanggal,
            bulan=bulan,
            tahun=tahun,
        )

        sql = f"""
            SELECT
                COUNT(*) AS total_transaksi,
                COUNT(DISTINCT joki_id) AS total_joki,
                COUNT(DISTINCT kloter_id) AS total_kloter,
                COALESCE(SUM(jumlah_judul), 0) AS total_judul,
                COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS total_pendapatan
            FROM catatan c
            {where_sql}
        """

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    @staticmethod
    def get_total_harian(tanggal: str):
        return RekapRepository._get_total(periode="harian", tanggal=tanggal)

    @staticmethod
    def get_total_bulanan(bulan: int, tahun: int):
        return RekapRepository._get_total(periode="bulanan", bulan=bulan, tahun=tahun)

    @staticmethod
    def get_total_tahunan(tahun: int):
        return RekapRepository._get_total(periode="tahunan", tahun=tahun)

    # ==========================================================
    # REKAP JOKI
    # ==========================================================

    @staticmethod
    def _get_rekap_joki(
        periode: str,
        tanggal: Optional[str] = None,
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        where_sql, params = RekapRepository._build_filter(
            periode=periode,
            tanggal=tanggal,
            bulan=bulan,
            tahun=tahun,
            alias="c",
        )

        sql = f"""
            SELECT
                j.id,
                j.kode,
                j.nama,
                j.harga_per_judul,
                COUNT(c.id) AS total_transaksi,
                COUNT(DISTINCT c.kloter_id) AS total_kloter,
                COALESCE(SUM(c.jumlah_judul), 0) AS jumlah_judul,
                COALESCE(SUM(c.jumlah_judul * c.harga_per_judul), 0) AS total_pendapatan
            FROM joki j
            LEFT JOIN catatan c ON c.joki_id = j.id
        """

        if where_sql:
            sql += "\n" + where_sql

        sql += """
            GROUP BY j.id, j.kode, j.nama, j.harga_per_judul
            ORDER BY total_pendapatan DESC, jumlah_judul DESC, j.nama ASC
        """

        if limit:
            sql += "\nLIMIT %s"
            params.append(limit)

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    @staticmethod
    def get_rekap_joki(tanggal: str, limit: Optional[int] = None):
        return RekapRepository._get_rekap_joki(periode="harian", tanggal=tanggal, limit=limit)

    @staticmethod
    def get_rekap_bulanan(bulan: int, tahun: int, limit: Optional[int] = None):
        return RekapRepository._get_rekap_joki(periode="bulanan", bulan=bulan, tahun=tahun, limit=limit)

    @staticmethod
    def get_rekap_tahunan(tahun: int, limit: Optional[int] = None):
        return RekapRepository._get_rekap_joki(periode="tahunan", tahun=tahun, limit=limit)

    # ==========================================================
    # REKAP KLOTER
    # ==========================================================

    @staticmethod
    def get_rekap_kloter(
        periode: str = "harian",
        tanggal: str | None = None,
        bulan: int | None = None,
        tahun: int | None = None,
        limit: int | None = None,
    ):
        periode = RekapRepository._validate_period(periode)
        
        sql = """
            SELECT
                k.id,
                k.kode,
                k.nama,
                COUNT(c.id) AS total_transaksi,
                COUNT(DISTINCT c.joki_id) AS total_joki,
                COALESCE(SUM(c.jumlah_judul), 0) AS jumlah_judul,
                COALESCE(SUM(c.jumlah_judul * c.harga_per_judul), 0) AS total_pendapatan
            FROM kloter k
            LEFT JOIN catatan c ON c.kloter_id = k.id
            WHERE 1=1
        """
        params = []

        if periode == "harian" and tanggal:
            sql += " AND c.tanggal = %s"
            params.append(tanggal)
        elif periode == "bulanan":
            if tahun:
                sql += " AND EXTRACT(YEAR FROM c.tanggal) = %s"
                params.append(tahun)
            if bulan:
                sql += " AND EXTRACT(MONTH FROM c.tanggal) = %s"
                params.append(bulan)
        elif periode == "tahunan" and tahun:
            sql += " AND EXTRACT(YEAR FROM c.tanggal) = %s"
            params.append(tahun)

        sql += """
            GROUP BY k.id, k.kode, k.nama, k.urutan
            ORDER BY k.urutan ASC
        """

        if limit:
            sql += " LIMIT %s"
            params.append(limit)

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    # ==========================================================
    # DETAIL JOKI
    # ==========================================================

    @staticmethod
    def get_detail_joki(
        joki_id: int,
        periode: str = "harian",
        tanggal: Optional[str] = None,
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
    ) -> list[dict]:
        """Get detail transaksi untuk joki tertentu."""
        where_sql, params = RekapRepository._build_filter(
            periode=periode,
            tanggal=tanggal,
            bulan=bulan,
            tahun=tahun,
            alias="c",
        )
        
        params.insert(0, joki_id)
        
        sql = f"""
            SELECT
                c.tanggal,
                c.jumlah_judul,
                c.harga_per_judul,
                c.jumlah_judul * c.harga_per_judul AS total,
                k.kode AS kloter_kode,
                k.nama AS kloter_nama
            FROM catatan c
            LEFT JOIN kloter k ON k.id = c.kloter_id
            WHERE c.joki_id = %s
        """
        
        if where_sql:
            sql += " AND " + where_sql.replace("WHERE ", "")
        
        sql += " ORDER BY c.tanggal DESC"
        
        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    # ==========================================================
    # DETAIL KLOTER
    # ==========================================================

    @staticmethod
    def get_detail_kloter(
        kloter_id: int,
        periode: str = "harian",
        tanggal: Optional[str] = None,
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
    ) -> list[dict]:
        """Get detail transaksi untuk kloter tertentu."""
        where_sql, params = RekapRepository._build_filter(
            periode=periode,
            tanggal=tanggal,
            bulan=bulan,
            tahun=tahun,
            alias="c",
        )
        
        params.insert(0, kloter_id)
        
        sql = f"""
            SELECT
                c.tanggal,
                c.jumlah_judul,
                c.harga_per_judul,
                c.jumlah_judul * c.harga_per_judul AS total,
                j.kode AS joki_kode,
                j.nama AS joki_nama
            FROM catatan c
            LEFT JOIN joki j ON j.id = c.joki_id
            WHERE c.kloter_id = %s
        """
        
        if where_sql:
            sql += " AND " + where_sql.replace("WHERE ", "")
        
        sql += " ORDER BY c.tanggal DESC"
        
        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    # ==========================================================
    # EXPORT
    # ==========================================================

    @staticmethod
    def export_rekap(
        periode: str = "harian",
        tanggal: Optional[str] = None,
        bulan: Optional[int] = None,
        tahun: Optional[int] = None,
    ) -> list[dict]:
        """Export data untuk periode tertentu."""
        where_sql, params = RekapRepository._build_filter(
            periode=periode,
            tanggal=tanggal,
            bulan=bulan,
            tahun=tahun,
            alias="c",
        )
        
        sql = f"""
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
            {where_sql}
            ORDER BY c.tanggal DESC
        """
        
        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    # ==========================================================
    # TREND
    # ==========================================================

    @staticmethod
    def get_trend(
        tahun: int,
        bulan: Optional[int] = None,
    ) -> list[dict]:
        """Get trend data untuk chart."""
        sql = """
            SELECT
                tanggal,
                COUNT(*) AS transaksi,
                COALESCE(SUM(jumlah_judul), 0) AS judul,
                COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS pendapatan
            FROM catatan
            WHERE EXTRACT(YEAR FROM tanggal) = %s
        """
        params = [tahun]
        
        if bulan is not None:
            sql += " AND EXTRACT(MONTH FROM tanggal) = %s"
            params.append(bulan)
        
        sql += " GROUP BY tanggal ORDER BY tanggal"
        
        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()