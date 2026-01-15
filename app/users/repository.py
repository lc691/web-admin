from datetime import datetime
from typing import Dict, List, Optional

from db.connect import get_db_cursor, get_dict_cursor


class UserRepository:

    def list(
        self,
        where_sql: str = "u.is_active = TRUE",
        params: dict | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:

        params = dict(params or {})
        params.update({"limit": limit, "offset": offset})

        query = f"""
            SELECT
                u.id,
                u.user_id,
                u.username,
                u.first_name,
                u.is_vip,
                u.vip_expired,
                u.is_active,
                u.created_at,
                COALESCE((
                    SELECT COUNT(*) 
                    FROM vip_logs v
                    WHERE v.target_user_id = u.user_id
                ), 0) AS total_purchases
            FROM users u
            WHERE {where_sql}
            ORDER BY u.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def get_by_id(self, id: int) -> Optional[Dict]:
        query = """
            SELECT
                u.id,
                u.user_id,
                u.username,
                u.first_name,
                u.is_vip,
                u.vip_expired,
                u.vip_start,
                u.is_active,
                COALESCE((
                    SELECT COUNT(*) 
                    FROM vip_logs v
                    WHERE v.target_user_id = u.user_id
                ), 0) AS total_purchases
            FROM users u
            WHERE u.id = %s
            LIMIT 1
        """

        with get_dict_cursor() as (cur, _):
            cur.execute(query, (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def create(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        is_vip: bool = False,
    ) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(
                """
                INSERT INTO users (user_id, username, first_name, is_vip)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
                """,
                (user_id, username, first_name, is_vip),
            )

    def update(
        self,
        id: int,
        username: Optional[str],
        is_vip: bool,
        vip_expired: Optional[datetime],
        is_active: bool,
    ) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(
                """
                UPDATE users
                SET
                    username = %s,
                    is_vip = %s,
                    vip_expired = %s,
                    is_active = %s
                WHERE id = %s
                """,
                (username, is_vip, vip_expired, is_active, id),
            )

    def delete(self, id: int) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("DELETE FROM users WHERE id = %s", (id,))
