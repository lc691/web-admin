from typing import Dict, List, Optional, Tuple

from db.connect import get_db_cursor, get_dict_cursor


class ShowRepository:
    """
    Repository layer for `shows` table.
    Handles CRUD operations and source label join.
    """

    # =====================================================
    # CONFIG
    # =====================================================
    TABLE_NAME = "shows"

    ALLOWED_UPDATE_FIELDS = {
        "title",
        "sinopsis",
        "genre",
        "source_id",
        "hashtags",
        "thumbnail_url",
        "is_adult",
    }

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================
    def _build_update_clause(self, data: Dict) -> Tuple[str, List]:
        """
        Build dynamic SET clause for UPDATE query.
        Returns:
            set_clause (str),
            values (list)
        """
        fields = []
        values = []

        for key, value in data.items():
            if key not in self.ALLOWED_UPDATE_FIELDS:
                continue

            fields.append(f"{key} = %s")
            values.append(value)

        if not fields:
            return "", []

        # auto updated_at
        fields.append("updated_at = NOW()")

        return ", ".join(fields), values

    # =====================================================
    # LIST ALL
    # =====================================================
    def list_all(self) -> List[Dict]:
        query = f"""
            SELECT 
                s.id,
                s.title,
                s.thumbnail_url,
                s.sinopsis,
                s.genre,
                s.hashtags,
                s.source_id,
                r.label AS source_label,
                s.is_adult
            FROM {self.TABLE_NAME} s
            LEFT JOIN request_sources r
                ON s.source_id = r.id
            ORDER BY s.id DESC
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query)
            return cur.fetchall()

    # =====================================================
    # GET BY ID
    # =====================================================
    def get_by_id(self, show_id: int) -> Optional[Dict]:
        if not isinstance(show_id, int) or show_id <= 0:
            return None

        query = f"""
            SELECT 
                s.*,
                r.label AS source_label
            FROM {self.TABLE_NAME} s
            LEFT JOIN request_sources r
                ON s.source_id = r.id
            WHERE s.id = %s
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query, (show_id,))
            return cur.fetchone()

    # =====================================================
    # INSERT
    # =====================================================
    def insert(self, data: Dict) -> int:
        """
        Insert new show.
        Returns inserted rowcount (1 if success).
        """
        if "title" not in data or not data["title"]:
            raise ValueError("title is required")

        query = f"""
            INSERT INTO {self.TABLE_NAME} (
                title,
                sinopsis,
                genre,
                hashtags,
                source_id,
                thumbnail_url,
                is_adult,
                posted_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
        """

        values = (
            data["title"],
            data.get("sinopsis"),
            data.get("genre"),
            data.get("hashtags"),
            data.get("source_id"),
            data.get("thumbnail_url"),
            data.get("is_adult", False),
        )

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, values)
            return cur.rowcount

    # =====================================================
    # UPDATE ONE
    # =====================================================
    def update_one(self, show_id: int, data: Dict) -> int:
        """
        Update single show by id.
        Returns affected row count.
        """
        if not isinstance(show_id, int) or show_id <= 0:
            return 0

        set_clause, values = self._build_update_clause(data)
        if not set_clause:
            return 0

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {set_clause}
            WHERE id = %s
        """

        values.append(show_id)

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, tuple(values))
            return cur.rowcount

    # =====================================================
    # UPDATE BULK
    # =====================================================
    def update_bulk(self, ids: List[int], data: Dict) -> int:
        """
        Update multiple shows by id list.
        Returns affected row count.
        """
        if not ids:
            return 0

        # Filter only valid ints
        ids = [i for i in ids if isinstance(i, int) and i > 0]
        if not ids:
            return 0

        set_clause, values = self._build_update_clause(data)
        if not set_clause:
            return 0

        placeholders = ",".join(["%s"] * len(ids))

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {set_clause}
            WHERE id IN ({placeholders})
        """

        values.extend(ids)

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, tuple(values))
            return cur.rowcount

    # =====================================================
    # DELETE
    # =====================================================
    def delete(self, show_id: int) -> int:
        """
        Delete show by id.
        Returns affected row count.
        """
        if not isinstance(show_id, int) or show_id <= 0:
            return 0

        query = f"DELETE FROM {self.TABLE_NAME} WHERE id = %s"

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, (show_id,))
            return cur.rowcount
