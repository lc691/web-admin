from typing import Dict, List, Optional

from app.core.database import get_dict_cursor, get_db_cursor


class FileRepository:
    TABLE_NAME = "files"

    # ==========================================================
    # LIST WITH PAGINATION
    # ==========================================================
    def list_all(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        show_id: int | None = None,
        file_type: str | None = None,
        is_paid: bool | None = None,
    ) -> dict:
        offset = (page - 1) * per_page

        # Build WHERE clause
        where_conditions = []
        params = []

        if search and len(search.strip()) >= 2:
            where_conditions.append(
                "(f.file_name ILIKE %s OR f.main_title ILIKE %s)"
            )
            search_term = f"%{search.strip()}%"
            params.extend([search_term, search_term])

        if show_id is not None:
            where_conditions.append("f.show_id = %s")
            params.append(show_id)

        if file_type is not None:
            where_conditions.append("f.file_type = %s")
            params.append(file_type)

        if is_paid is not None:
            where_conditions.append("f.is_paid = %s")
            params.append(is_paid)

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # COUNT TOTAL
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self.TABLE_NAME} f
            {where_clause}
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(count_query, tuple(params))
            total = cur.fetchone()["total"]

        if total == 0:
            return {
                "data": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
            }

        # MAIN QUERY
        query = f"""
            SELECT
                f.id,
                f.file_name,
                f.file_type,
                f.is_paid,
                f.main_title,
                f.channel_username,
                f.message_id,
                f.show_id,
                f.file_id,
                f.file_size,
                f.date_added,
                s.title AS show_title,
                COUNT(sf.id) AS show_count
            FROM {self.TABLE_NAME} f
            LEFT JOIN shows s ON f.show_id = s.id
            LEFT JOIN show_files sf ON sf.file_id = f.id
            {where_clause}
            GROUP BY f.id, s.title
            ORDER BY f.id DESC
            LIMIT %s OFFSET %s
        """

        params.extend([per_page, offset])

        with get_dict_cursor() as (cur, _):
            cur.execute(query, tuple(params))
            data = cur.fetchall()

        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    # ==========================================================
    # LIST SIMPLE
    # ==========================================================
    def list_simple(
        self,
        show_id: int | None = None,
    ) -> List[Dict]:
        query = f"""
            SELECT
                f.id,
                f.file_name,
                f.file_type,
                f.is_paid,
                f.main_title,
                f.channel_username,
                f.message_id,
                f.show_id,
                f.file_id
            FROM {self.TABLE_NAME} f
        """
        params = []

        if show_id is not None:
            query += " WHERE f.show_id = %s"
            params.append(show_id)

        query += " ORDER BY f.id DESC"

        with get_dict_cursor() as (cur, _):
            cur.execute(query, tuple(params))
            return cur.fetchall()

    # ==========================================================
    # GET BY ID
    # ==========================================================
    def get_by_id(self, file_id: int) -> Optional[Dict]:
        query = f"""
            SELECT
                f.id,
                f.file_name,
                f.file_type,
                f.is_paid,
                f.main_title,
                f.channel_username,
                f.message_id,
                f.show_id,
                f.file_id,
                f.file_size,
                f.date_added,
                f.free_hash,
                f.paid_hash,
                s.title AS show_title,
                COUNT(sf.id) AS show_count
            FROM {self.TABLE_NAME} f
            LEFT JOIN shows s ON f.show_id = s.id
            LEFT JOIN show_files sf ON sf.file_id = f.id
            WHERE f.id = %s
            GROUP BY f.id, s.title
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query, (file_id,))
            return cur.fetchone()

    # ==========================================================
    # GET BY SHOW ID
    # ==========================================================
    def get_by_show_id(self, show_id: int) -> List[Dict]:
        query = f"""
            SELECT
                f.id,
                f.file_name,
                f.file_type,
                f.is_paid,
                f.main_title,
                f.channel_username,
                f.message_id,
                f.file_id,
                sf.alias_name
            FROM {self.TABLE_NAME} f
            LEFT JOIN show_files sf ON sf.file_id = f.id
            WHERE f.show_id = %s
            ORDER BY f.id DESC
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query, (show_id,))
            return cur.fetchall()

    # ==========================================================
    # CREATE
    # ==========================================================
    def create(self, data: dict) -> Dict:
        allowed_fields = [
            "file_name",
            "file_type",
            "is_paid",
            "main_title",
            "channel_username",
            "message_id",
            "show_id",
            "file_id",
            "file_size",
            "free_hash",
            "paid_hash",
            "main_title_normalized",
        ]

        fields = []
        placeholders = []
        values = []

        for field in allowed_fields:
            if field in data:
                fields.append(field)
                placeholders.append("%s")
                values.append(data[field])

        if not fields:
            raise ValueError("No valid fields provided")

        query = f"""
            INSERT INTO {self.TABLE_NAME}
            ({", ".join(fields)})
            VALUES ({", ".join(placeholders)})
            RETURNING *
        """

        with get_db_cursor(commit=True) as (cur, conn):
            cur.execute(query, tuple(values))
            result = cur.fetchone()
            conn.commit()
            return result

    # ==========================================================
    # UPDATE
    # ==========================================================
    def update(self, file_id: int, data: dict) -> Optional[Dict]:
        if not data:
            return self.get_by_id(file_id)

        # Get current show_id (READ)
        with get_dict_cursor() as (cur, _):
            cur.execute(
                "SELECT show_id FROM files WHERE id = %s",
                (file_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            old_show_id = row["show_id"]

        # UPDATE (WRITE)
        with get_db_cursor(commit=True) as (cur, conn):
            fields = []
            values = []

            allowed_update_fields = [
                "file_name",
                "file_type",
                "is_paid",
                "main_title",
                "channel_username",
                "message_id",
                "show_id",
                "file_id",
                "file_size",
                "free_hash",
                "paid_hash",
                "main_title_normalized",
            ]

            for key, value in data.items():
                if key in allowed_update_fields:
                    fields.append(f"{key} = %s")
                    values.append(value)

            if not fields:
                return self.get_by_id(file_id)

            values.append(file_id)

            query = f"""
                UPDATE {self.TABLE_NAME}
                SET {", ".join(fields)}
                WHERE id = %s
                RETURNING *
            """

            cur.execute(query, tuple(values))
            updated = cur.fetchone()

            # SYNC show_files (jika show_id berubah)
            if "show_id" in data:
                new_show_id = data.get("show_id")

                if old_show_id != new_show_id:
                    if old_show_id is not None:
                        cur.execute(
                            """
                            DELETE FROM show_files
                            WHERE file_id = %s AND show_id = %s
                            """,
                            (file_id, old_show_id),
                        )

                    if new_show_id is not None:
                        cur.execute(
                            """
                            INSERT INTO show_files (show_id, file_id, message_id)
                            SELECT show_id, id, message_id
                            FROM files
                            WHERE id = %s
                            ON CONFLICT (show_id, file_id) DO NOTHING
                            """,
                            (file_id,),
                        )

            conn.commit()
            return updated

    # ==========================================================
    # DELETE
    # ==========================================================
    def delete(self, file_id: int) -> bool:
        query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"

        with get_db_cursor(commit=True) as (cur, conn):
            cur.execute(query, (file_id,))
            result = cur.rowcount > 0
            conn.commit()
            return result

    # ==========================================================
    # COUNT
    # ==========================================================
    def count(self, show_id: int | None = None) -> int:
        query = f"SELECT COUNT(*) AS total FROM {self.TABLE_NAME}"
        params = []

        if show_id is not None:
            query += " WHERE show_id = %s"
            params.append(show_id)

        with get_dict_cursor() as (cur, _):
            cur.execute(query, tuple(params))
            result = cur.fetchone()
            return result["total"] if result else 0

    # ==========================================================
    # GET USAGE COUNT
    # ==========================================================
    def get_usage_count(self, file_id: int) -> int:
        query = "SELECT COUNT(*) FROM show_files WHERE file_id = %s"

        with get_dict_cursor() as (cur, _):
            cur.execute(query, (file_id,))
            return cur.fetchone()["count"]

    # ==========================================================
    # SYNC SHOW FILES
    # ==========================================================
    def sync_show_files(self, show_id: int) -> int:
        with get_db_cursor(commit=True) as (cur, conn):
            # Validasi show ada
            cur.execute(
                "SELECT title FROM shows WHERE id = %s",
                (show_id,),
            )
            row = cur.fetchone()
            if not row:
                return -1

            show_title = row[0]  # ✅ tuple, pakai indeks

            # 1️⃣ Insert relasi baru
            cur.execute(
                """
                INSERT INTO show_files (show_id, file_id, message_id, alias_name)
                SELECT 
                    f.show_id,
                    f.id,
                    f.message_id,
                    f.main_title
                FROM files f
                WHERE f.show_id = %s
                ON CONFLICT (show_id, file_id)
                DO NOTHING
                """,
                (show_id,),
            )
            inserted = cur.rowcount

            # 2️⃣ Isi files.main_title jika kosong
            cur.execute(
                """
                UPDATE files
                SET main_title = %s
                WHERE show_id = %s
                  AND (main_title IS NULL OR main_title = '')
                """,
                (f"🎬 {show_title}", show_id),
            )

            # 3️⃣ Isi alias_name jika kosong
            cur.execute(
                """
                UPDATE show_files sf
                SET alias_name = f.main_title
                FROM files f
                WHERE sf.file_id = f.id
                  AND sf.show_id = %s
                  AND (sf.alias_name IS NULL OR sf.alias_name = '')
                  AND f.main_title IS NOT NULL
                """,
                (show_id,),
            )

            conn.commit()
            return inserted

    # ==========================================================
    # BULK DELETE
    # ==========================================================
    def bulk_delete(self, file_ids: list[int]) -> int:
        if not file_ids:
            return 0

        placeholders = ",".join(["%s"] * len(file_ids))
        query = f"DELETE FROM {self.TABLE_NAME} WHERE id IN ({placeholders})"

        with get_db_cursor(commit=True) as (cur, conn):
            cur.execute(query, tuple(file_ids))
            result = cur.rowcount
            conn.commit()
            return result

    # ==========================================================
    # GET STATS
    # ==========================================================
    def get_stats(self) -> dict:
        query = f"""
            SELECT
                COUNT(*) AS total_files,
                COUNT(CASE WHEN is_paid = TRUE THEN 1 END) AS paid_files,
                COUNT(CASE WHEN is_paid = FALSE THEN 1 END) AS free_files,
                COUNT(DISTINCT show_id) AS used_shows,
                COUNT(DISTINCT channel_username) AS unique_channels
            FROM {self.TABLE_NAME}
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query)
            return cur.fetchone()