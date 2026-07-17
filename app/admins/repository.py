from typing import Dict, List, Optional

from app.core.database import get_dict_cursor


class AdminRepository:
    TABLE_NAME = "admins"

    # =========================
    # CREATE
    # =========================
    def create(
        self,
        user_id: int,
        first_name: str,
        username: str,
        is_active: bool = True,
    ) -> Dict:
        query = f"""
            INSERT INTO {self.TABLE_NAME}
                (user_id, first_name, username, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """

        with get_dict_cursor(commit=True) as (cursor, conn):
            cursor.execute(
                query,
                (user_id, first_name, username, is_active),
            )
            return cursor.fetchone()

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            WHERE user_id = %s
        """

        with get_dict_cursor() as (cursor, _):
            cursor.execute(query, (user_id,))
            return cursor.fetchone()

    # =========================
    # GET BY USERNAME
    # =========================
    def get_by_username(self, username: str) -> Optional[Dict]:
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            WHERE username = %s
        """

        with get_dict_cursor() as (cursor, _):
            cursor.execute(query, (username,))
            return cursor.fetchone()

    # =========================
    # LIST ALL
    # =========================
    def list_all(
        self,
        only_active: bool = False,
    ) -> List[Dict]:
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
        """
        params = []

        if only_active:
            query += " WHERE is_active = true"
            params.append(only_active)

        query += " ORDER BY user_id DESC"

        with get_dict_cursor() as (cursor, _):
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        username: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict]:
        fields = []
        params = []

        if first_name is not None:
            fields.append("first_name = %s")
            params.append(first_name)

        if username is not None:
            fields.append("username = %s")
            params.append(username)

        if is_active is not None:
            fields.append("is_active = %s")
            params.append(is_active)

        if not fields:
            return self.get_by_id(user_id)

        params.append(user_id)

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {', '.join(fields)}
            WHERE user_id = %s
            RETURNING *
        """

        with get_dict_cursor(commit=True) as (cursor, conn):
            cursor.execute(query, tuple(params))
            return cursor.fetchone()

    # =========================
    # DELETE
    # =========================
    def delete(self, user_id: int) -> bool:
        query = f"""
            DELETE FROM {self.TABLE_NAME}
            WHERE user_id = %s
        """

        with get_dict_cursor(commit=True) as (cursor, conn):
            cursor.execute(query, (user_id,))
            return cursor.rowcount > 0

    # =========================
    # ACTIVATE / DEACTIVATE
    # =========================
    def set_active(self, user_id: int, is_active: bool) -> Optional[Dict]:
        return self.update(user_id, is_active=is_active)

    # =========================
    # COUNT
    # =========================
    def count(self, only_active: bool = False) -> int:
        query = f"""
            SELECT COUNT(*) AS total
            FROM {self.TABLE_NAME}
        """
        params = []

        if only_active:
            query += " WHERE is_active = true"
            params.append(only_active)

        with get_dict_cursor() as (cursor, _):
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return result["total"] if result else 0

    # =========================
    # EXISTS
    # =========================
    def exists(self, user_id: int) -> bool:
        result = self.get_by_id(user_id)
        return result is not None