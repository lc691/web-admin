from db.connect import get_db_cursor, get_dict_cursor


def get_all_users():
    with get_db_cursor() as (cursor, _):
        cursor.execute("SELECT id, user_id, username, is_vip, vip_expired FROM users ORDER BY id DESC")
        return cursor.fetchall()

def get_user_by_id(id: int):
    with get_db_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        return cursor.fetchone()


def create_user(user_id, username, first_name, is_vip=False):
    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, is_vip)
            VALUES (%s, %s, %s, %s)
        """, (user_id, username, first_name, is_vip))


def update_user(id, username, is_vip, vip_expired):
    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute("""
            UPDATE users
            SET username = %s, is_vip = %s, vip_expired = %s
            WHERE id = %s
        """, (username, is_vip, vip_expired, id))


def delete_user(user_id: int):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
