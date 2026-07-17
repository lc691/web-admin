from typing import Optional

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class JokiRepository:
    """
    Repository untuk Master Joki.
    Menangani operasi CRUD (Create, Read, Update, Delete) 
    dan operasi khusus lainnya untuk tabel joki.
    """

    # ==========================================================
    # READ
    # ==========================================================

    @staticmethod
    def get_all(keyword: Optional[str] = None):
        """
        Mengambil seluruh data joki dengan opsi pencarian berdasarkan keyword.
        """
        sql = """
            SELECT
                id,
                kode,
                nama,
                harga_per_judul,
                no_hp,
                keterangan,
                aktif,
                created_at,
                updated_at
            FROM joki
        """

        params = []

        if keyword:
            sql += """
                WHERE LOWER(kode) LIKE LOWER(%s)
                   OR LOWER(nama) LIKE LOWER(%s)
            """
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        sql += " ORDER BY nama ASC"

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    @staticmethod
    def get_paginated(
        page: int = 1,
        per_page: int = 20,
        keyword: Optional[str] = None,
        aktif: Optional[bool] = None,
    ) -> dict:
        """
        Mengambil data joki dengan pagination.
        """
        offset = (page - 1) * per_page
        
        where_conditions = []
        params = []
        
        if keyword:
            where_conditions.append(
                "(LOWER(kode) LIKE LOWER(%s) OR LOWER(nama) LIKE LOWER(%s))"
            )
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern])
        
        if aktif is not None:
            where_conditions.append("aktif = %s")
            params.append(aktif)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Count total
        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM joki
            {where_clause}
        """
        
        with get_clean_dict_cursor() as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()["total"]
        
        if total == 0:
            return {
                "data": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
            }
        
        # Main query
        sql = f"""
            SELECT
                id,
                kode,
                nama,
                harga_per_judul,
                no_hp,
                keterangan,
                aktif,
                created_at,
                updated_at
            FROM joki
            {where_clause}
            ORDER BY nama ASC
            LIMIT %s OFFSET %s
        """
        
        params.extend([per_page, offset])
        
        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            data = cur.fetchall()
        
        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_by_id(joki_id: int):
        with get_clean_dict_cursor() as cur:
            cur.execute("SELECT * FROM joki WHERE id = %s", (joki_id,))
            return cur.fetchone()

    @staticmethod
    def get_by_kode(kode: str) -> Optional[dict]:
        """Mengambil data joki berdasarkan kode."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                "SELECT * FROM joki WHERE LOWER(kode) = LOWER(%s)",
                (kode,)
            )
            return cur.fetchone()

    @staticmethod
    def get_by_name(nama: str) -> Optional[dict]:
        """Mengambil data joki berdasarkan nama."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                "SELECT * FROM joki WHERE LOWER(nama) = LOWER(%s)",
                (nama,)
            )
            return cur.fetchone()

    @staticmethod
    def get_by_ids(ids: list[int]) -> list[dict]:
        """Mengambil data joki berdasarkan list ID."""
        if not ids:
            return []
        
        placeholders = ",".join(["%s"] * len(ids))
        with get_clean_dict_cursor() as cur:
            cur.execute(
                f"SELECT * FROM joki WHERE id IN ({placeholders}) ORDER BY nama ASC",
                ids,
            )
            return cur.fetchall()

    @staticmethod
    def get_harga(joki_id: int):
        with get_clean_dict_cursor() as cur:
            cur.execute(
                "SELECT harga_per_judul FROM joki WHERE id = %s",
                (joki_id,)
            )
            row = cur.fetchone()
            return row["harga_per_judul"] if row else 0

    @staticmethod
    def get_name(joki_id: int):
        with get_clean_dict_cursor() as cur:
            cur.execute(
                "SELECT nama FROM joki WHERE id = %s",
                (joki_id,)
            )
            row = cur.fetchone()
            return row["nama"] if row else None

    @staticmethod
    def get_active():
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT id, nama, harga_per_judul
                FROM joki
                WHERE aktif = TRUE
                ORDER BY nama
                """
            )
            return cur.fetchall()

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        kode: str,
        nama: str,
        harga_per_judul: float,
        no_hp: str = "",
        keterangan: str = "",
        aktif: bool = True,
    ):
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO joki (kode, nama, harga_per_judul, no_hp, keterangan, aktif)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (kode, nama, harga_per_judul, no_hp, keterangan, aktif),
            )
            new_id = cur.fetchone()["id"]

        log.info(f"[JOKI] berhasil tambah id={new_id}")
        return new_id

    # ==========================================================
    # UPDATE
    # ==========================================================

    @staticmethod
    def update(
        joki_id: int,
        kode: str,
        nama: str,
        harga_per_judul: float,
        no_hp: str,
        keterangan: str,
        aktif: bool,
    ):
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE joki
                SET
                    kode = %s,
                    nama = %s,
                    harga_per_judul = %s,
                    no_hp = %s,
                    keterangan = %s,
                    aktif = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (kode, nama, harga_per_judul, no_hp, keterangan, aktif, joki_id),
            )

        log.info(f"[JOKI] update id={joki_id}")

    @staticmethod
    def bulk_update_status(ids: list[int], aktif: bool) -> int:
        """Update status multiple joki."""
        if not ids:
            return 0
        
        placeholders = ",".join(["%s"] * len(ids))
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                f"""
                UPDATE joki
                SET aktif = %s, updated_at = NOW()
                WHERE id IN ({placeholders})
                """,
                [aktif] + ids,
            )
            updated = cur.rowcount
        
        log.info(f"[JOKI] bulk update status {updated} joki to {aktif}")
        return updated

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(joki_id: int):
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                "DELETE FROM joki WHERE id = %s",
                (joki_id,),
            )
        log.info(f"[JOKI] delete id={joki_id}")

    # ==========================================================
    # TOGGLE
    # ==========================================================

    @staticmethod
    def toggle_status(joki_id: int):
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE joki
                SET aktif = NOT aktif, updated_at = NOW()
                WHERE id = %s
                RETURNING aktif
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            return result["aktif"] if result else None

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists_nama(nama: str, exclude_id: Optional[int] = None) -> bool:
        sql = "SELECT 1 FROM joki WHERE LOWER(nama) = LOWER(%s)"
        params = [nama]

        if exclude_id is not None:
            sql += " AND id <> %s"
            params.append(exclude_id)

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone() is not None

    @staticmethod
    def exists_kode(kode: str, exclude_id: Optional[int] = None) -> bool:
        sql = "SELECT 1 FROM joki WHERE LOWER(kode) = LOWER(%s)"
        params = [kode]

        if exclude_id is not None:
            sql += " AND id <> %s"
            params.append(exclude_id)

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone() is not None

    # ==========================================================
    # STATISTICS
    # ==========================================================

    @staticmethod
    def get_statistics():
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE aktif = TRUE) AS aktif,
                    COUNT(*) FILTER (WHERE aktif = FALSE) AS nonaktif,
                    COALESCE(MIN(harga_per_judul), 0) AS harga_terendah,
                    COALESCE(MAX(harga_per_judul), 0) AS harga_tertinggi,
                    COALESCE(ROUND(AVG(harga_per_judul), 0), 0) AS rata_harga,
                    COALESCE(
                        (SELECT COUNT(DISTINCT joki_id) FROM catatan),
                        0
                    ) AS digunakan
                FROM joki
                """
            )
            return cur.fetchone()