from db.connect import get_db_cursor, get_dict_cursor
from typing import Optional

def get_all_files():
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM files ORDER BY id DESC")
        return cur.fetchall()


def get_file_by_id(file_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM files WHERE id = %s", (file_id,))
        return cur.fetchone()


def insert_file(
    file_id: str, file_name: str, free_hash: str, paid_hash: str,
    channel_username: str, file_type: str, file_size: int,
    message_id: int, main_title: str = None, show_id: int = None
):
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO files (
                file_id, file_name, free_hash, paid_hash,
                channel_username, file_type, file_size,
                message_id, main_title, show_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            file_id, file_name, free_hash, paid_hash,
            channel_username, file_type, file_size,
            message_id, main_title, show_id
        ))
        return cur.fetchone()[0]


def update_file(
    id: int, file_name: str, channel_username: str,
    file_type: str, main_title: str, show_id: int = None
):
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE files SET
                file_name = %s,
                channel_username = %s,
                file_type = %s,
                main_title = %s,
                show_id = %s
            WHERE id = %s
        """, (file_name, channel_username, file_type, main_title, show_id, id))


def delete_file(id: int):
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM files WHERE id = %s", (id,))


def update_file_by_id(
    file_id: int,
    file_name: str,
    file_type: str,
    file_size: int,
    main_title: str,
    channel_username: str,
    message_id: Optional[int],
    show_id: Optional[int]
):

    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("""
            UPDATE files SET
                file_name = %s,
                file_type = %s,
                file_size = %s,
                main_title = %s,
                channel_username = %s,
                message_id = %s,
                show_id = %s
            WHERE id = %s
        """, (
            file_name,
            file_type,
            file_size,
            main_title,
            channel_username,
            message_id if message_id else None,
            show_id if show_id else None,
            file_id
        ))
