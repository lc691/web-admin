from configs.logging_setup import log
from db.connect import get_db_cursor, get_dict_cursor


def get_admin_actions(
    limit: int = 50,
    offset: int = 0,
    admin_id: int | None = None,
    action: str | None = None,
):
    """
    Ambil admin audit logs dengan filter & pagination
    """

    query = """
        SELECT
            admin_id,
            action,
            target_type,
            target_id,
            created_at
        FROM admin_audit_logs
        WHERE 1=1
    """
    params = []

    if admin_id:
        query += " AND admin_id = %s"
        params.append(admin_id)

    if action:
        query += " AND action = %s"
        params.append(action)

    query += """
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    with get_dict_cursor() as (cursor, _):
        cursor.execute(query, params)
        return cursor.fetchall()


def log_admin_action(
    admin_id: int,
    action: str,
    target_type: str,
    target_id: int | None = None,
    notes: str | None = None,
):
    """
    Centralized admin audit logger.
    HARUS dipanggil untuk semua aksi admin penting.
    """

    try:
        with get_db_cursor(commit=True) as (cursor, _):
            cursor.execute(
                """
                INSERT INTO admin_audit_logs (
                    admin_id,
                    action,
                    target_type,
                    target_id,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    admin_id,
                    action,
                    target_type,
                    target_id,
                    notes,
                ),
            )

        log.info(
            f"[ADMIN_AUDIT] admin={admin_id} action={action} "
            f"target={target_type}:{target_id}"
        )

    except Exception as e:
        # ❗ PENTING: JANGAN PERNAH raise
        log.error(
            f"[ADMIN_AUDIT] FAILED admin={admin_id} action={action}: {e}",
            exc_info=True,
        )
