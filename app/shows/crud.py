# crud.py
from db.connect import get_dict_cursor, get_db_cursor

# CREATE
def create_show(data):
    with get_db_cursor() as (cur, conn):
        cur.execute("""
            INSERT INTO shows (title, sinopsis, genre, hashtags, thumbnail, is_adult)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get("title"),
            data.get("sinopsis"),
            data.get("genre"),
            data.get("hashtags"),
            data.get("thumbnail"),
            data.get("is_adult", False)
        ))
        conn.commit()


# READ - Semua
def get_all_shows():
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM shows ORDER BY id DESC")
        return cur.fetchall()


# READ - By ID
def get_show_by_id(show_id):
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT * FROM shows WHERE id = %s", (show_id,))
        return cur.fetchone()


# UPDATE
def update_show(show_id, data):
    with get_db_cursor() as (cur, conn):
        is_adult = bool(data.get("is_adult", False))  # konversi ke boolean

        cur.execute("""
            UPDATE shows SET
                title = %s,
                sinopsis = %s,
                genre = %s,
                hashtags = %s,
                thumbnail = %s,
                is_adult = %s
            WHERE id = %s
        """, (
            data.get("title"),
            data.get("sinopsis"),
            data.get("genre"),
            data.get("hashtags"),
            data.get("thumbnail"),
            is_adult,
            show_id
        ))
        conn.commit()

# DELETE
def delete_show(show_id):
    with get_db_cursor() as (cur, conn):
        cur.execute("DELETE FROM shows WHERE id = %s", (show_id,))
        conn.commit()
