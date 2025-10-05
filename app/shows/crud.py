from db.connect import get_dict_cursor, get_db_cursor

# CREATE
def create_show(data):
    with get_db_cursor() as (cur, conn):
        cur.execute("""
            INSERT INTO shows (title, sinopsis, genre, hashtags, thumbnail_url, is_adult)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get("title"),
            data.get("sinopsis"),
            data.get("genre"),
            data.get("hashtags"),
            data.get("thumbnail_url"),
            data.get("is_adult", False)
        ))
        conn.commit()


# READ - Semua (⚠️ hanya untuk internal, tidak dipakai list besar)
def get_all_shows():
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM shows ORDER BY id DESC")
        return cur.fetchall()


# 🆕 READ - Paginasi
def get_shows_paginated(limit: int, offset: int):
    """
    Ambil data shows dengan paginasi dan total count.
    Return: (rows: list[dict], total: int)
    """
    query = """
        SELECT *, COUNT(*) OVER() AS total_count
        FROM shows
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """
    with get_dict_cursor() as (cur, _):
        cur.execute(query, (limit, offset))
        rows = cur.fetchall()
        total = rows[0]["total_count"] if rows else 0
        return rows, total


# READ - By ID
def get_show_by_id(show_id):
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM shows WHERE id = %s", (show_id,))
        return cur.fetchone()


# UPDATE
def update_show(show_id, data):
    with get_db_cursor() as (cur, conn):
        is_adult = bool(data.get("is_adult", False))
        cur.execute("""
            UPDATE shows SET
                title = %s,
                sinopsis = %s,
                genre = %s,
                hashtags = %s,
                thumbnail_url = %s,
                is_adult = %s
            WHERE id = %s
        """, (
            data.get("title"),
            data.get("sinopsis"),
            data.get("genre"),
            data.get("hashtags"),
            data.get("thumbnail_url"),
            is_adult,
            show_id
        ))
        conn.commit()


# DELETE
def delete_show(show_id):
    with get_db_cursor() as (cur, conn):
        cur.execute("DELETE FROM shows WHERE id = %s", (show_id,))
        conn.commit()


def delete_show_by_id(show_id: int) -> None:
    query = "DELETE FROM shows WHERE id = %s"
    with get_db_cursor(commit=True) as (cursor, conn):
        cursor.execute(query, (show_id,))


# ADD
def insert_show(show_data: dict) -> int:
    """
    Menyimpan show baru ke tabel shows.
    Return: id show yang baru dibuat.
    """
    query = """
        INSERT INTO shows (title, sinopsis, genre, hashtags, thumbnail_url, is_adult, posted_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        RETURNING id
    """
    values = (
        show_data.get("title"),
        show_data.get("sinopsis"),
        show_data.get("genre"),
        show_data.get("hashtags"),
        show_data.get("thumbnail_url"),
        show_data.get("is_adult", False),
    )
    with get_db_cursor(commit=True) as (cursor, conn):
        cursor.execute(query, values)
        new_id = cursor.fetchone()[0]
    return new_id
