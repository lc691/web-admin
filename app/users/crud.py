from datetime import datetime
from typing import Dict, List, Optional

from db.connect import get_db_cursor, get_dict_cursor


# =========================
# GET USERS (LIST)
# =========================
def get_users(
    where_sql: str = "u.is_active = TRUE",
    params: dict | None = None,
    limit: int = 100,
    offset: int = 0,
    
) -> List[Dict]:
    if params is None:
        params = {}

    params.update({"limit": limit, "offset": offset})

    query = f"""
        SELECT
            u.id,
            u.user_id,
            u.username,
            u.first_name,
            u.is_vip,
            u.vip_expired,
            COALESCE(v.vip_count, 0) AS vip_purchases,
            u.is_active,
            u.created_at
        FROM users u
        LEFT JOIN (
            SELECT user_id, COUNT(*) AS vip_count
            FROM vip_transactions
            GROUP BY user_id
        ) v ON v.user_id = u.user_id
        WHERE {where_sql}
        ORDER BY u.id DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(query, params)
        rows = cursor.fetchall()

    # 🔹 Konversi DictRow ke dict biasa supaya template bisa pakai dot
    return [dict(row) for row in rows]


# =========================
# GET USER BY ID
# =========================
def get_user_by_id(id: int) -> Optional[Dict]:
    query = """
        SELECT
            u.id,
            u.user_id,
            u.username,
            u.first_name,
            u.is_vip,
            u.vip_expired,
            COALESCE(v.vip_count, 0) AS vip_purchases,
            u.vip_start,
            u.is_active
        FROM users u
        LEFT JOIN (
            SELECT user_id, COUNT(*) AS vip_count
            FROM vip_transactions
            GROUP BY user_id
        ) v ON v.user_id = u.user_id
        WHERE u.id = %s
        LIMIT 1
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(query, (id,))
        row = cursor.fetchone()

    return dict(row) if row else None


# ==========================================================
# CREATE USER
# ==========================================================


def create_user(
    user_id: int,
    username: Optional[str],
    first_name: Optional[str],
    is_vip: bool = False,
):
    """
    Tambah user baru (aman dari duplikat user_id)
    """
    query = """
        INSERT INTO users (user_id, username, first_name, is_vip)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """

    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute(
            query,
            (user_id, username, first_name, is_vip),
        )


# ==========================================================
# UPDATE USER
# ==========================================================


def update_user(
    id: int,
    username: Optional[str],
    is_vip: bool,
    vip_expired: Optional[datetime],
    is_active: bool,
):
    """
    Update user (dipanggil dari edit form)
    """
    query = """
        UPDATE users
        SET
            username = %s,
            is_vip = %s,
            vip_expired = %s,
            is_active = %s
        WHERE id = %s
    """

    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute(
            query,
            (username, is_vip, vip_expired, is_active, id),
        )


# ==========================================================
# DELETE USER
# ==========================================================


def delete_user(id: int):
    """
    Hapus user (hard delete)
    """
    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute(
            "DELETE FROM users WHERE id = %s",
            (id,),
        )
