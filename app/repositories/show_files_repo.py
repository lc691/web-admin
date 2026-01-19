from db.connect import get_dict_cursor


def list_show_files():
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                sf.id AS show_file_id,
                s.title AS show_title,
                f.file_name,
                sf.show_id,
                sf.message_id
            FROM show_files sf
            JOIN files f ON f.id = sf.file_id
            JOIN shows s ON s.id = sf.show_id
            ORDER BY sf.id DESC
            """
        )
        return cur.fetchall()


def get_show_file(show_file_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                sf.id,
                sf.show_id,
                sf.message_id,
                s.title AS show_title,
                f.file_name
            FROM show_files sf
            JOIN files f ON f.id = sf.file_id
            JOIN shows s ON s.id = sf.show_id
            WHERE sf.id = %s
            """,
            (show_file_id,),
        )
        return cur.fetchone()


def update_show_file(show_file_id: int, alias_name: str, message_id: int | None):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            UPDATE show_files SET
                alias_name = %s,
                message_id = %s
            WHERE id = %s
            """,
            (alias_name, message_id, show_file_id),
        )
        conn.commit()
