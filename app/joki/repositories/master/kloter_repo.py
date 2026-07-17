from typing import Optional

from app.utils.logger import log
from app.core.database import get_clean_dict_cursor


class KloterRepository:
    """Repository Master Kloter."""

    # ==========================================================
    # READ
    # ==========================================================

    @staticmethod
    def get_all(keyword: Optional[str] = None):
        """Mengambil seluruh data kloter dengan opsi pencarian."""
        sql = """
            SELECT
                id,
                kode,
                nama,
                keterangan,
                urutan,
                aktif,
                created_at,
                updated_at
            FROM kloter
        """

        params = []

        if keyword:
            sql += """
                WHERE LOWER(kode) LIKE LOWER(%s)
                   OR LOWER(nama) LIKE LOWER(%s)
            """
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        sql += " ORDER BY urutan ASC, nama ASC"

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    # ==========================================================
    # GET ALL WITH PAGINATION
    # ==========================================================

    @staticmethod
    def get_all_paginated(
        keyword: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> dict:
        """
        Mengambil data kloter dengan pagination.
        
        Returns:
            dict: {
                "data": list[dict],
                "total": int,
                "page": int,
                "per_page": int,
                "total_pages": int
            }
        """
        offset = (page - 1) * per_page
        
        # Count query
        sql_count = "SELECT COUNT(*) as total FROM kloter"
        params = []
        
        if keyword:
            where_clause = """
                WHERE LOWER(kode) LIKE LOWER(%s)
                OR LOWER(nama) LIKE LOWER(%s)
            """
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern])
            sql_count += where_clause
        
        with get_clean_dict_cursor() as cur:
            cur.execute(sql_count, params if keyword else [])
            total = cur.fetchone()["total"]
        
        if total == 0:
            return {
                "data": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
            }
        
        # Data query
        sql_data = """
            SELECT
                id,
                kode,
                nama,
                keterangan,
                urutan,
                aktif,
                created_at,
                updated_at
            FROM kloter
        """
        
        data_params = []
        
        if keyword:
            where_clause = """
                WHERE LOWER(kode) LIKE LOWER(%s)
                OR LOWER(nama) LIKE LOWER(%s)
            """
            keyword_pattern = f"%{keyword}%"
            data_params.extend([keyword_pattern, keyword_pattern])
            sql_data += where_clause
        
        sql_data += " ORDER BY urutan ASC, nama ASC LIMIT %s OFFSET %s"
        data_params.extend([per_page, offset])
        
        with get_clean_dict_cursor() as cur:
            cur.execute(sql_data, data_params)
            data = cur.fetchall()
        
        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    
    @staticmethod
    def get_active():
        """Mengambil seluruh kloter aktif."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT id, kode, nama
                FROM kloter
                WHERE aktif = TRUE
                ORDER BY urutan, nama
                """
            )
            return cur.fetchall()

    @staticmethod
    def get_by_id(kloter_id: int):
        """Mengambil data kloter berdasarkan ID."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                "SELECT * FROM kloter WHERE id = %s",
                (kloter_id,),
            )
            return cur.fetchone()

    @staticmethod
    def get_by_kode(kode: str) -> Optional[dict]:
        """Mengambil data kloter berdasarkan kode."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                "SELECT * FROM kloter WHERE LOWER(kode) = LOWER(%s)",
                (kode,)
            )
            return cur.fetchone()

    @staticmethod
    def get_by_name(nama: str) -> Optional[dict]:
        """Mengambil data kloter berdasarkan nama."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                "SELECT * FROM kloter WHERE LOWER(nama) = LOWER(%s)",
                (nama,)
            )
            return cur.fetchone()

    @staticmethod
    def get_by_ids(ids: list[int]) -> list[dict]:
        """Mengambil data kloter berdasarkan list ID."""
        if not ids:
            return []
        
        placeholders = ",".join(["%s"] * len(ids))
        with get_clean_dict_cursor() as cur:
            cur.execute(
                f"""
                SELECT *
                FROM kloter
                WHERE id IN ({placeholders})
                ORDER BY urutan ASC, nama ASC
                """,
                ids,
            )
            return cur.fetchall()

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        kode: str,
        nama: str,
        keterangan: str = "",
        urutan: int = 0,
        aktif: bool = True,
    ):
        """Menambahkan data kloter baru."""
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO kloter (kode, nama, keterangan, urutan, aktif)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (kode, nama, keterangan, urutan, aktif),
            )
            new_id = cur.fetchone()["id"]

        log.info(f"[KLOTER] tambah id={new_id}")
        return new_id

    # ==========================================================
    # UPDATE
    # ==========================================================

    @staticmethod
    def update(
        kloter_id: int,
        kode: str,
        nama: str,
        keterangan: str,
        urutan: int,
        aktif: bool,
    ):
        """Mengubah data kloter yang sudah ada."""
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE kloter
                SET
                    kode = %s,
                    nama = %s,
                    keterangan = %s,
                    urutan = %s,
                    aktif = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (kode, nama, keterangan, urutan, aktif, kloter_id),
            )

        log.info(f"[KLOTER] update id={kloter_id}")

    @staticmethod
    def bulk_update_status(ids: list[int], aktif: bool) -> int:
        """Update status multiple kloter."""
        if not ids:
            return 0
        
        placeholders = ",".join(["%s"] * len(ids))
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                f"""
                UPDATE kloter
                SET aktif = %s, updated_at = NOW()
                WHERE id IN ({placeholders})
                """,
                [aktif] + ids,
            )
            updated = cur.rowcount
        
        log.info(f"[KLOTER] bulk update status {updated} kloter to {aktif}")
        return updated

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(kloter_id: int):
        """Menghapus data kloter berdasarkan ID."""
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                "DELETE FROM kloter WHERE id = %s",
                (kloter_id,),
            )
        log.info(f"[KLOTER] delete id={kloter_id}")

    # ==========================================================
    # TOGGLE
    # ==========================================================

    @staticmethod
    def toggle_status(kloter_id: int):
        """Mengubah status aktif/nonaktif kloter."""
        with get_clean_dict_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE kloter
                SET aktif = NOT aktif, updated_at = NOW()
                WHERE id = %s
                RETURNING aktif
                """,
                (kloter_id,),
            )
            result = cur.fetchone()
            aktif = result["aktif"] if result else None

        log.info(f"[KLOTER] toggle id={kloter_id} aktif={aktif}")
        return aktif

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists_nama(nama: str, exclude_id: Optional[int] = None) -> bool:
        """Cek apakah nama kloter sudah ada."""
        sql = "SELECT 1 FROM kloter WHERE LOWER(nama) = LOWER(%s)"
        params = [nama]

        if exclude_id is not None:
            sql += " AND id <> %s"
            params.append(exclude_id)

        with get_clean_dict_cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone() is not None

    @staticmethod
    def exists_kode(kode: str, exclude_id: Optional[int] = None) -> bool:
        """Cek apakah kode kloter sudah ada."""
        sql = "SELECT 1 FROM kloter WHERE LOWER(kode) = LOWER(%s)"
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
        """Statistik master kloter."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE aktif = TRUE) AS aktif,
                    COUNT(*) FILTER (WHERE aktif = FALSE) AS nonaktif
                FROM kloter
                """
            )
            return cur.fetchone()

    @staticmethod
    def get_statistics_detailed() -> dict:
        """Statistik detail kloter termasuk yang digunakan di catatan."""
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE aktif = TRUE) AS aktif,
                    COUNT(*) FILTER (WHERE aktif = FALSE) AS nonaktif,
                    COALESCE(
                        (SELECT COUNT(DISTINCT kloter_id) FROM catatan),
                        0
                    ) AS digunakan
                FROM kloter
                """
            )
            return cur.fetchone()