# app/source/crud.py
from typing import Optional

from db.connect import get_dict_cursor


def get_all_sources():
    """
    Ambil semua source dari database
    """
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM source ORDER BY id ASC")
        return cur.fetchall()


def get_source_by_id(source_id: int) -> Optional[dict]:
    """
    Ambil satu source berdasarkan ID
    """
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM source WHERE id = %s", (source_id,))
        return cur.fetchone()


def create_source(name: str):
    """
    Tambah source baru
    """
    with get_dict_cursor() as (cur, conn):
        cur.execute("INSERT INTO source (name) VALUES (%s)", (name,))
        conn.commit()


def update_source_by_id(source_id: int, name: str):
    """
    Update nama source berdasarkan ID
    """
    with get_dict_cursor() as (cur, conn):
        cur.execute("UPDATE source SET name = %s WHERE id = %s", (name, source_id))
        conn.commit()


def delete_source(source_id: int):
    """
    Hapus source berdasarkan ID
    """
    with get_dict_cursor() as (cur, conn):
        cur.execute("DELETE FROM source WHERE id = %s", (source_id,))
        conn.commit()
