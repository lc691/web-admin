from datetime import datetime
from typing import Dict, List, Optional

from db.connect import get_db_cursor, get_dict_cursor

# ==========================================================
# GET USER LIST (UNTUK ADMIN / LIST PAGE)
# ==========================================================


def get_users(
    where_sql: str = "is_active = TRUE",
    params: dict | None = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict]:
    """
    Ambil list user dengan filter + pagination
    """
    if params is None:
        params = {}

    params.update(
        {
            "limit": limit,
            "offset": offset,
        }
    )

    query = f"""
        SELECT
            id,
            user_id,
            username,
            first_name,
            is_vip,
            vip_expired,
            is_active,
            created_at
        FROM users
        WHERE {where_sql}
        ORDER BY id DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(query, params)
        return cursor.fetchall()


# ==========================================================
# GET USER BY ID (EDIT PAGE)
# ==========================================================


def get_user_by_id(id: int) -> Optional[Dict]:
    """
    Ambil 1 user untuk edit (kolom lengkap yang dibutuhkan form)
    """
    query = """
        SELECT
            id,
            user_id,
            username,
            first_name,
            is_vip,
            vip_expired,
            vip_start,
            is_active
        FROM users
        WHERE id = %s
        LIMIT 1
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(query, (id,))
        return cursor.fetchone()


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
