from typing import Dict, List, Optional

from db.connect import get_clean_dict_cursor


class RequiredChannelRepository:
    TABLE_NAME = "required_channels"

    # =========================
    # CREATE
    # =========================
    def create(
        self,
        *,
        username: str,
        bot_username: str,
        added_by: Optional[str],
        is_active: bool = True,
    ) -> Dict:
        query = f"""
            INSERT INTO {self.TABLE_NAME}
                (username, bot_username, added_by, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """

        with get_clean_dict_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (username, bot_username, added_by, is_active),
            )
            return cursor.fetchone()

    # =========================
    # GET BY ID
    # =========================
    def get_by_id(self, channel_id: int) -> Optional[Dict]:
        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            WHERE id = %s
        """

        with get_clean_dict_cursor() as cursor:
            cursor.execute(query, (channel_id,))
            return cursor.fetchone()

    # =========================
    # LIST
    # =========================
    def list_all(
        self,
        *,
        bot_username: Optional[str] = None,
        only_active: bool = False,
    ) -> List[Dict]:
        conditions = []
        params = []

        if bot_username:
            conditions.append("bot_username = %s")
            params.append(bot_username)

        if only_active:
            conditions.append("is_active = true")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT *
            FROM {self.TABLE_NAME}
            {where_clause}
            ORDER BY added_at DESC
        """

        with get_clean_dict_cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        channel_id: int,
        *,
        username: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict]:

        fields = []
        params = []

        if username is not None:
            fields.append("username = %s")
            params.append(username)

        if is_active is not None:
            fields.append("is_active = %s")
            params.append(is_active)

        if not fields:
            return self.get_by_id(channel_id)

        params.append(channel_id)

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING *
        """

        with get_clean_dict_cursor(commit=True) as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchone()

    # =========================
    # DELETE (HARD)
    # =========================
    def delete(self, channel_id: int) -> bool:
        query = f"""
            DELETE FROM {self.TABLE_NAME}
            WHERE id = %s
        """

        with get_clean_dict_cursor(commit=True) as cursor:
            cursor.execute(query, (channel_id,))
            return cursor.rowcount > 0

    # =========================
    # SOFT DELETE
    # =========================
    def deactivate(self, channel_id: int) -> Optional[Dict]:
        return self.update(channel_id, is_active=False)