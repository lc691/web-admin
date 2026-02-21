from db.connect import get_dict_cursor


# =========================
# 📋 Semua Admin Actions
# =========================
def get_all_admin_actions():
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                aaa.id,
                aaa.admin_id,
                u.username AS admin_username,
                aaa.action,
                aaa.target_type,
                aaa.target_id,
                aaa.notes,
                aaa.created_at
            FROM affiliate_admin_actions aaa
            LEFT JOIN users u ON u.user_id = aaa.admin_id
            ORDER BY aaa.created_at DESC
        """)
        return cur.fetchall()


# =========================
# 👤 Actions by Admin
# =========================
def get_actions_by_admin(admin_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                aaa.id,
                aaa.action,
                aaa.target_type,
                aaa.target_id,
                aaa.notes,
                aaa.created_at
            FROM affiliate_admin_actions aaa
            WHERE aaa.admin_id = %s
            ORDER BY aaa.created_at DESC
        """,
            (admin_id,),
        )
        return cur.fetchall()


# =========================
# 🎯 Actions by Target
# =========================
def get_actions_by_target(target_type: str, target_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                aaa.id,
                aaa.admin_id,
                u.username AS admin_username,
                aaa.action,
                aaa.notes,
                aaa.created_at
            FROM affiliate_admin_actions aaa
            LEFT JOIN users u ON u.user_id = aaa.admin_id
            WHERE aaa.target_type = %s
              AND aaa.target_id = %s
            ORDER BY aaa.created_at DESC
        """,
            (target_type, target_id),
        )
        return cur.fetchall()


# =========================
# ➕ Create Admin Action Log
# =========================
def create_admin_action(
    admin_id: int,
    action: str,
    target_type: str,
    target_id: int,
    notes: str | None = None,
):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            INSERT INTO affiliate_admin_actions (
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

        action_id = cur.fetchone()["id"]
        conn.commit()
        return action_id
