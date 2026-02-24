from db.connect import get_dict_cursor

# =========================
# CONSTANTS
# =========================

ALLOWED_UPDATE_FIELDS = {
    "alias_name",
    "message_id",
    "show_id",
}


# =========================
# READ OPERATIONS
# =========================


def list_show_files() -> list[dict]:
    """
    Return all show_files with joined show & file info.
    """
    query = """
        SELECT
            sf.id AS show_file_id,
            s.title AS show_title,
            f.file_name,
            r.label AS source_label,
            sf.show_id,
            sf.message_id
        FROM show_files sf
        JOIN shows s
            ON s.id = sf.show_id
        LEFT JOIN request_sources r
            ON s.source_id = r.id
        JOIN files f
            ON f.id = sf.file_id
        ORDER BY sf.id DESC
    """

    with get_dict_cursor() as (cur, _):
        cur.execute(query)
        return cur.fetchall()


def get_show_file(show_file_id: int) -> dict | None:
    """
    Return single show_file by id.
    """
    if not isinstance(show_file_id, int) or show_file_id <= 0:
        return None

    query = """
        SELECT
            sf.id,
            sf.show_id,
            sf.message_id,
            s.title AS show_title,
            f.file_name,
            sf.alias_name
        FROM show_files sf
        JOIN files f ON f.id = sf.file_id
        JOIN shows s ON s.id = sf.show_id
        WHERE sf.id = %s
    """

    with get_dict_cursor() as (cur, _):
        cur.execute(query, (show_file_id,))
        return cur.fetchone()


# =========================
# UPDATE OPERATION
# =========================
def update_show_file(show_file_id: int, data: dict) -> int:
    """
    Update show_file by id.
    Returns affected row count.
    """

    if not isinstance(show_file_id, int) or show_file_id <= 0:
        return 0

    if not data:
        return 0

    fields = []
    values = []

    # Sanitasi alias_name
    if "alias_name" in data:
        alias = data.get("alias_name")
        cleaned = alias.strip() if alias else None
        data["alias_name"] = cleaned if cleaned else None

    # Build safe update fields
    for key, value in data.items():
        if key not in ALLOWED_UPDATE_FIELDS:
            continue

        fields.append(f"{key} = %s")
        values.append(value)

    if not fields:
        return 0

    values.append(show_file_id)

    query = f"""
        UPDATE show_files
        SET {", ".join(fields)}
        WHERE id = %s
    """

    with get_dict_cursor() as (cur, conn):
        cur.execute(query, tuple(values))
        conn.commit()
        return cur.rowcount


def update_show_files_bulk(ids: list[int], data: dict) -> int:
    """
    Update multiple show_files by id list.
    Returns affected row count.
    """

    if not ids:
        return 0

    valid_ids = [i for i in ids if isinstance(i, int) and i > 0]
    if not valid_ids:
        return 0

    fields = []
    values = []

    # Sanitasi alias_name
    if "alias_name" in data:
        alias = data.get("alias_name")
        cleaned = alias.strip() if alias else None
        data["alias_name"] = cleaned if cleaned else None

    for key, value in data.items():
        if key not in ALLOWED_UPDATE_FIELDS:
            continue
        fields.append(f"{key} = %s")
        values.append(value)

    if not fields:
        return 0

    placeholders = ",".join(["%s"] * len(valid_ids))
    values.extend(valid_ids)

    query = f"""
        UPDATE show_files
        SET {", ".join(fields)}
        WHERE id IN ({placeholders})
    """

    with get_dict_cursor() as (cur, conn):
        cur.execute(query, tuple(values))
        conn.commit()
        return cur.rowcount


# =========================
# DELETE OPERATION
# =========================
def delete_show_files_bulk(ids: list[int]) -> int:
    """
    Delete multiple show_files by id list.
    Returns affected row count.
    """

    if not ids:
        return 0

    valid_ids = [i for i in ids if isinstance(i, int) and i > 0]
    if not valid_ids:
        return 0

    placeholders = ",".join(["%s"] * len(valid_ids))

    query = f"""
        DELETE FROM show_files
        WHERE id IN ({placeholders})
    """

    with get_dict_cursor() as (cur, conn):
        cur.execute(query, tuple(valid_ids))
        conn.commit()
        return cur.rowcount
