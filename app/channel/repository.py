from typing import Any

from psycopg2 import errors

from db.connect import get_db_cursor, get_dict_cursor


class ChannelAdminRepository:
    TABLE_NAME = "channel_admin"

    # ==============================
    # CREATE
    # ==============================
    def create(
        self,
        nama_variabel: str,
        nilai: int,
        alias: str | None = None,
        keterangan: str | None = None,
        is_active: bool = False,
        created_by: int | None = None,
    ) -> int:

        if not nama_variabel or not isinstance(nilai, int):
            raise ValueError("Invalid nama_variabel or nilai")

        query = f"""
            INSERT INTO {self.TABLE_NAME}
            (nama_variabel, nilai, alias, keterangan, is_active, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        try:
            with get_db_cursor(commit=True) as (cur, _):
                if is_active:
                    cur.execute(f"UPDATE {self.TABLE_NAME} SET is_active = FALSE")

                cur.execute(
                    query,
                    (nama_variabel, nilai, alias, keterangan, is_active, created_by),
                )

                return cur.fetchone()[0]

        except errors.UniqueViolation:
            raise ValueError("Alias already exists")

    # ==============================
    # READ
    # ==============================
    def get_all(self) -> list[dict]:
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            ORDER BY id
        """
        with get_dict_cursor() as (cur, _):
            cur.execute(query)
            return cur.fetchall()

    def get_by_id(self, channel_id: int) -> dict | None:
        if channel_id <= 0:
            return None

        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            WHERE id = %s
        """
        with get_dict_cursor() as (cur, _):
            cur.execute(query, (channel_id,))
            return cur.fetchone()

    def get_active(self) -> dict | None:
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            WHERE is_active = TRUE
            LIMIT 1
        """
        with get_dict_cursor() as (cur, _):
            cur.execute(query)
            return cur.fetchone()

    # ==============================
    # UPDATE (Partial)
    # ==============================
    def update(self, channel_id: int, data: dict[str, Any]) -> int:

        if channel_id <= 0:
            raise ValueError("Invalid channel_id")

        if not data:
            return 0

        allowed_fields = {
            "nama_variabel",
            "nilai",
            "alias",
            "keterangan",
            "is_active",
        }

        set_clauses = []
        values = []

        for key, value in data.items():
            if key not in allowed_fields:
                continue
            set_clauses.append(f"{key} = %s")
            values.append(value)

        if not set_clauses:
            return 0

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """

        values.append(channel_id)

        try:
            with get_db_cursor(commit=True) as (cur, _):

                # Jika set is_active true → reset dulu
                if data.get("is_active") is True:
                    cur.execute(f"UPDATE {self.TABLE_NAME} SET is_active = FALSE")

                cur.execute(query, tuple(values))
                return cur.rowcount

        except errors.UniqueViolation:
            raise ValueError("Alias already exists")

    # ==============================
    # SET ACTIVE (Safe)
    # ==============================
    def set_active(self, channel_id: int) -> None:

        if channel_id <= 0:
            raise ValueError("Invalid channel_id")

        with get_db_cursor(commit=True) as (cur, _):

            # Pastikan ID ada dulu
            cur.execute(
                f"SELECT 1 FROM {self.TABLE_NAME} WHERE id = %s",
                (channel_id,),
            )
            if not cur.fetchone():
                raise ValueError("Channel not found")

            cur.execute(f"UPDATE {self.TABLE_NAME} SET is_active = FALSE")
            cur.execute(
                f"UPDATE {self.TABLE_NAME} SET is_active = TRUE WHERE id = %s",
                (channel_id,),
            )

    # ==============================
    # DELETE
    # ==============================
    def delete(self, channel_id: int) -> int:

        if channel_id <= 0:
            return 0

        query = f"""
            DELETE FROM {self.TABLE_NAME}
            WHERE id = %s
        """
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(query, (channel_id,))
            return cur.rowcount

    # ==============================
    # SEARCH
    # ==============================
    def search(
        self,
        keyword: str | None = None,
        is_active: bool | None = None,
    ) -> list[dict]:

        conditions = []
        values = []

        if keyword:
            conditions.append("(alias ILIKE %s OR nama_variabel ILIKE %s)")
            values.extend([f"%{keyword}%", f"%{keyword}%"])

        if is_active is not None:
            conditions.append("is_active = %s")
            values.append(is_active)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            {where_clause}
            ORDER BY id
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query, tuple(values))
            return cur.fetchall()
