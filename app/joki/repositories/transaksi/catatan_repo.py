from datetime import date
from typing import Optional

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class CatatanRepository:
    """
    Repository Transaksi Catatan Harian.

    Bertanggung jawab terhadap:
    - CRUD Catatan
    - Filter transaksi
    - Validasi transaksi

    Tidak menangani:
    - Dashboard
    - Rekap
    - Statistik
    """

    # ==========================================================
    # GET ALL
    # ==========================================================

    @staticmethod
    def get_all(
        tanggal: Optional[str] = None,
        joki_id: Optional[int] = None,
        kloter_id: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        sql = """
            SELECT
                c.id,
                c.tanggal,
                c.joki_id,
                j.nama AS nama_joki,
                c.kloter_id,
                k.nama AS nama_kloter,
                c.jumlah_judul,
                c.harga_per_judul,
                (c.jumlah_judul * c.harga_per_judul) AS total,
                c.keterangan,
                c.created_at,
                c.updated_at
            FROM catatan c
            INNER JOIN joki j ON j.id = c.joki_id
            INNER JOIN kloter k ON k.id = c.kloter_id
            WHERE 1=1
        """

        params = []

        if tanggal:
            sql += " AND c.tanggal = %s"
            params.append(tanggal)

        if joki_id:
            sql += " AND c.joki_id = %s"
            params.append(joki_id)

        if kloter_id:
            sql += " AND c.kloter_id = %s"
            params.append(kloter_id)

        if keyword:
            sql += """
                AND (
                    LOWER(j.nama) LIKE LOWER(%s)
                    OR LOWER(k.nama) LIKE LOWER(%s)
                    OR LOWER(COALESCE(c.keterangan, '')) LIKE LOWER(%s)
                )
            """
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        sql += """
            ORDER BY c.tanggal DESC, j.nama ASC, k.urutan ASC, c.id ASC
            LIMIT %s OFFSET %s
        """

        offset = (page - 1) * per_page
        params.extend([per_page, offset])

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            items = cur.fetchall()

        # Total data
        sql_total = """
            SELECT COUNT(*) AS total
            FROM catatan c
            INNER JOIN joki j ON j.id = c.joki_id
            INNER JOIN kloter k ON k.id = c.kloter_id
            WHERE 1=1
        """
        total_params = []

        if tanggal:
            sql_total += " AND c.tanggal = %s"
            total_params.append(tanggal)

        if joki_id:
            sql_total += " AND c.joki_id = %s"
            total_params.append(joki_id)

        if kloter_id:
            sql_total += " AND c.kloter_id = %s"
            total_params.append(kloter_id)

        if keyword:
            sql_total += """
                AND (
                    LOWER(j.nama) LIKE LOWER(%s)
                    OR LOWER(k.nama) LIKE LOWER(%s)
                    OR LOWER(COALESCE(c.keterangan, '')) LIKE LOWER(%s)
                )
            """
            total_params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

        with get_clean_dict_cursor() as cur:
            cur.execute(sql_total, total_params)
            total = cur.fetchone()["total"]

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    # ==========================================================
    # GET BY ID
    # ==========================================================

    @staticmethod
    def get_by_id(catatan_id: int):
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.*,
                    j.nama AS nama_joki,
                    k.nama AS nama_kloter,
                    (c.jumlah_judul * c.harga_per_judul) AS total
                FROM catatan c
                INNER JOIN joki j ON j.id = c.joki_id
                INNER JOIN kloter k ON k.id = c.kloter_id
                WHERE c.id = %s
                """,
                (catatan_id,),
            )
            return cur.fetchone()

    # ==========================================================
    # GET BY DATE RANGE
    # ==========================================================

    @staticmethod
    def get_by_date_range(
        start_date: str,
        end_date: str,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        offset = (page - 1) * per_page

        sql = """
            SELECT
                c.id,
                c.tanggal,
                c.joki_id,
                j.nama AS nama_joki,
                c.kloter_id,
                k.nama AS nama_kloter,
                c.jumlah_judul,
                c.harga_per_judul,
                (c.jumlah_judul * c.harga_per_judul) AS total,
                c.keterangan
            FROM catatan c
            INNER JOIN joki j ON j.id = c.joki_id
            INNER JOIN kloter k ON k.id = c.kloter_id
            WHERE c.tanggal BETWEEN %s AND %s
            ORDER BY c.tanggal DESC, j.nama ASC, k.urutan ASC
            LIMIT %s OFFSET %s
        """

        params = [start_date, end_date, per_page, offset]

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            items = cur.fetchall()

        sql_total = """
            SELECT COUNT(*) AS total
            FROM catatan c
            WHERE c.tanggal BETWEEN %s AND %s
        """

        with get_clean_dict_cursor() as cur:
            cur.execute(sql_total, [start_date, end_date])
            total = cur.fetchone()["total"]

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    # ==========================================================
    # GET BY JOKI
    # ==========================================================

    @staticmethod
    def get_by_joki(
        joki_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        offset = (page - 1) * per_page

        sql = """
            SELECT
                c.id,
                c.tanggal,
                c.joki_id,
                j.nama AS nama_joki,
                c.kloter_id,
                k.nama AS nama_kloter,
                c.jumlah_judul,
                c.harga_per_judul,
                (c.jumlah_judul * c.harga_per_judul) AS total,
                c.keterangan
            FROM catatan c
            INNER JOIN joki j ON j.id = c.joki_id
            INNER JOIN kloter k ON k.id = c.kloter_id
            WHERE c.joki_id = %s
        """
        params = [joki_id]

        if start_date:
            sql += " AND c.tanggal >= %s"
            params.append(start_date)

        if end_date:
            sql += " AND c.tanggal <= %s"
            params.append(end_date)

        sql += " ORDER BY c.tanggal DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            items = cur.fetchall()

        sql_total = """
            SELECT COUNT(*) AS total
            FROM catatan c
            WHERE c.joki_id = %s
        """
        total_params = [joki_id]

        if start_date:
            sql_total += " AND c.tanggal >= %s"
            total_params.append(start_date)

        if end_date:
            sql_total += " AND c.tanggal <= %s"
            total_params.append(end_date)

        with get_clean_dict_cursor() as cur:
            cur.execute(sql_total, total_params)
            total = cur.fetchone()["total"]

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    # ==========================================================
    # GET BY KLOTER
    # ==========================================================

    @staticmethod
    def get_by_kloter(
        kloter_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        offset = (page - 1) * per_page

        sql = """
            SELECT
                c.id,
                c.tanggal,
                c.joki_id,
                j.nama AS nama_joki,
                c.kloter_id,
                k.nama AS nama_kloter,
                c.jumlah_judul,
                c.harga_per_judul,
                (c.jumlah_judul * c.harga_per_judul) AS total,
                c.keterangan
            FROM catatan c
            INNER JOIN joki j ON j.id = c.joki_id
            INNER JOIN kloter k ON k.id = c.kloter_id
            WHERE c.kloter_id = %s
        """
        params = [kloter_id]

        if start_date:
            sql += " AND c.tanggal >= %s"
            params.append(start_date)

        if end_date:
            sql += " AND c.tanggal <= %s"
            params.append(end_date)

        sql += " ORDER BY c.tanggal DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            items = cur.fetchall()

        sql_total = """
            SELECT COUNT(*) AS total
            FROM catatan c
            WHERE c.kloter_id = %s
        """
        total_params = [kloter_id]

        if start_date:
            sql_total += " AND c.tanggal >= %s"
            total_params.append(start_date)

        if end_date:
            sql_total += " AND c.tanggal <= %s"
            total_params.append(end_date)

        with get_clean_dict_cursor() as cur:
            cur.execute(sql_total, total_params)
            total = cur.fetchone()["total"]

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        tanggal: str,
        joki_id: int,
        kloter_id: int,
        jumlah_judul: int,
        keterangan: str = "",
    ):
        from ..master.joki_repo import JokiRepository

        harga_per_judul = JokiRepository.get_harga(joki_id)

        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO catatan
                (tanggal, joki_id, kloter_id, jumlah_judul, harga_per_judul, keterangan, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
                """,
                (tanggal, joki_id, kloter_id, jumlah_judul, harga_per_judul, keterangan),
            )
            new_id = cur.fetchone()["id"]

        log.info(f"[CATATAN] tambah id={new_id}")
        return new_id

    # ==========================================================
    # UPDATE
    # ==========================================================

    @staticmethod
    def update(
        catatan_id: int,
        tanggal: str,
        joki_id: int,
        kloter_id: int,
        jumlah_judul: int,
        keterangan: str = "",
    ):
        from ..master.joki_repo import JokiRepository

        harga_per_judul = JokiRepository.get_harga(joki_id)

        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE catatan
                SET
                    tanggal = %s,
                    joki_id = %s,
                    kloter_id = %s,
                    jumlah_judul = %s,
                    harga_per_judul = %s,
                    keterangan = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (tanggal, joki_id, kloter_id, jumlah_judul, harga_per_judul, keterangan, catatan_id),
            )

        log.info(f"[CATATAN] update id={catatan_id}")

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(catatan_id: int):
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                "DELETE FROM catatan WHERE id = %s",
                (catatan_id,),
            )

        log.info(f"[CATATAN] delete id={catatan_id}")

    # ==========================================================
    # BULK DELETE
    # ==========================================================

    @staticmethod
    def bulk_delete(ids: list[int]) -> int:
        """Menghapus multiple catatan sekaligus."""
        if not ids:
            return 0

        placeholders = ",".join(["%s"] * len(ids))
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                f"DELETE FROM catatan WHERE id IN ({placeholders})",
                ids,
            )
            deleted = cur.rowcount

        log.info(f"[CATATAN] bulk delete: {deleted} catatan dihapus")
        return deleted

    # ==========================================================
    # GET LAST
    # ==========================================================

    @staticmethod
    def get_last_id():
        with get_clean_dict_cursor() as cur:
            cur.execute("SELECT id FROM catatan ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            return row["id"] if row else None

    @staticmethod
    def get_last_transaction():
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.*,
                    j.nama AS nama_joki,
                    k.nama AS nama_kloter,
                    (c.jumlah_judul * c.harga_per_judul) AS total
                FROM catatan c
                INNER JOIN joki j ON j.id = c.joki_id
                INNER JOIN kloter k ON k.id = c.kloter_id
                ORDER BY c.id DESC
                LIMIT 1
                """
            )
            return cur.fetchone()

    # ==========================================================
    # SUMMARY
    # ==========================================================

    @staticmethod
    def get_summary_by_date(tanggal: str) -> dict:
        """Mendapatkan ringkasan catatan untuk satu tanggal."""
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
                WHERE tanggal = %s
                """,
                (tanggal,)
            )
            return cur.fetchone()

    # ==========================================================
    # TREND
    # ==========================================================

    @staticmethod
    def get_daily_trend(start_date: str, end_date: str) -> list[dict]:
        """Mendapatkan trend harian untuk chart."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    tanggal,
                    COUNT(*) AS transaksi,
                    COALESCE(SUM(jumlah_judul), 0) AS judul,
                    COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS pendapatan
                FROM catatan
                WHERE tanggal BETWEEN %s AND %s
                GROUP BY tanggal
                ORDER BY tanggal
                """,
                (start_date, end_date),
            )
            return cur.fetchall()

    # ==========================================================
    # STATISTICS
    # ==========================================================

    @staticmethod
    def get_statistics() -> dict:
        """Mendapatkan statistik keseluruhan."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_transaksi,
                    COALESCE(SUM(jumlah_judul), 0) AS total_judul,
                    COALESCE(SUM(jumlah_judul * harga_per_judul), 0) AS total_pendapatan,
                    COUNT(DISTINCT joki_id) AS total_joki,
                    COUNT(DISTINCT kloter_id) AS total_kloter,
                    COALESCE(MIN(tanggal), CURRENT_DATE) AS tanggal_pertama,
                    COALESCE(MAX(tanggal), CURRENT_DATE) AS tanggal_terakhir
                FROM catatan
                """
            )
            return cur.fetchone()

    # ==========================================================
    # COUNT
    # ==========================================================

    @staticmethod
    def count():
        with get_clean_dict_cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM catatan")
            return cur.fetchone()["total"]