from db.connect import get_db_cursor, get_dict_cursor


def list_files():
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                f.id,
                f.file_name,
                f.file_type,
                f.is_paid,
                f.main_title,
                f.show_id,
                COUNT(sf.id) AS show_count
            FROM files f
            LEFT JOIN show_files sf ON sf.file_id = f.id
            GROUP BY f.id
            ORDER BY f.id DESC
            """
        )
        return cur.fetchall()


def get_file(file_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                f.*,
                COUNT(sf.id) AS show_count
            FROM files f
            LEFT JOIN show_files sf ON sf.file_id = f.id
            WHERE f.id = %s
            GROUP BY f.id
            """,
            (file_id,),
        )
        return cur.fetchone()


def update_file(file_id: int, data: dict):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            UPDATE files SET
                file_name = %s,
                main_title = %s,
                is_paid = %s,
            WHERE id = %s
            """,
            (
                data["file_name"],
                data["main_title"],
                data["is_paid"],
                file_id,
            ),
        )
        conn.commit()


def get_file_usage_count(file_id: int) -> int:
    with get_dict_cursor() as (cur, _):
        cur.execute(
            "SELECT COUNT(*) FROM show_files WHERE file_id = %s",
            (file_id,),
        )
        return cur.fetchone()["count"]


def delete_file(file_id: int):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            "DELETE FROM files WHERE id = %s",
            (file_id,),
        )
        conn.commit()
