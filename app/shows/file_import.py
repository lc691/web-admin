from db.connect import get_db_cursor, get_dict_cursor


def import_show_files(
    source_show_id: int,
    target_show_id: int,
    message_id: int,
) -> int:
    """
    Copy files dari source_show ke target_show
    return: jumlah row yang diinsert
    """
    sql = """
        INSERT INTO show_files (show_id, file_id, message_id)
        SELECT %s, f.id, %s
        FROM files f
        WHERE f.show_id = %s
        AND NOT EXISTS (
            SELECT 1 FROM show_files sf
            WHERE sf.show_id = %s
            AND sf.file_id = f.id
        )
    """

    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute(
            sql,
            (
                target_show_id,
                message_id,
                source_show_id,
                target_show_id,
            ),
        )
        return cursor.rowcount


def count_files_in_show(show_id: int) -> int:
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            "SELECT COUNT(*) AS total FROM files WHERE show_id = %s",
            (show_id,),
        )
        return cursor.fetchone()["total"]
