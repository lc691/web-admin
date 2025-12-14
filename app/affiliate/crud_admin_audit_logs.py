from typing import Optional

from db.connect import get_dict_cursor

ALLOWED_TARGET_TYPES = {
    "user",
    "affiliate",
    "withdraw",
    "commission",
    "admin",
    "audit_log",
}


BASE_SELECT = """
    SELECT
        aal.id,
        aal.admin_id,
        a.username AS admin_username,
        aal.action,
        aal.target_type,
        aal.target_id,
        aal.notes,
        aal.created_at
    FROM affiliate_admin_audit_logs aal
    LEFT JOIN admins a ON a.user_id = aal.admin_id
"""


def get_all_audit_logs(limit: int = 500):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            BASE_SELECT
            + """
            ORDER BY aal.created_at DESC
            LIMIT %s
        """,
            (limit,),
        )
        return cur.fetchall()


def get_audit_logs_by_admin(admin_id: int, limit: int = 200):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            BASE_SELECT
            + """
            WHERE aal.admin_id = %s
            ORDER BY aal.created_at DESC
            LIMIT %s
        """,
            (admin_id, limit),
        )
        return cur.fetchall()


def get_audit_logs_by_target(
    target_type: str,
    target_id: int,
    limit: int = 200,
):
    if target_type not in ALLOWED_TARGET_TYPES:
        raise ValueError(f"Invalid target_type: {target_type}")

    with get_dict_cursor() as (cur, _):
        cur.execute(
            BASE_SELECT
            + """
            WHERE aal.target_type = %s
              AND aal.target_id = %s
            ORDER BY aal.created_at DESC
            LIMIT %s
        """,
            (target_type, target_id, limit),
        )
        return cur.fetchall()


def create_audit_log(
    admin_id: int,
    action: str,
    target_type: str,
    target_id: int,
    notes: Optional[str] = None,
):
    if target_type not in ALLOWED_TARGET_TYPES:
        raise ValueError(f"Invalid target_type: {target_type}")

    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            INSERT INTO affiliate_admin_audit_logs (
                admin_id,
                action,
                target_type,
                target_id,
                notes
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """,
            (admin_id, action, target_type, target_id, notes),
        )

        audit_id = cur.fetchone()["id"]
        conn.commit()
        return audit_id
