from db.connect import get_dict_cursor


# =========================
# 📋 Semua Abuse Logs
# =========================
def get_all_abuse_logs():
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                aal.id,
                aal.user_id,
                u1.username AS username,

                aal.referrer_user_id,
                u2.username AS referrer_username,

                aal.event_type,
                aal.reason,
                aal.severity,
                aal.metadata,
                aal.created_at
            FROM affiliate_abuse_logs aal
            LEFT JOIN users u1 ON u1.user_id = aal.user_id
            LEFT JOIN users u2 ON u2.user_id = aal.referrer_user_id
            ORDER BY aal.created_at DESC
        """
        )
        return cur.fetchall()


# =========================
# 👤 Abuse Logs by User
# =========================
def get_abuse_logs_by_user(user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                aal.id,
                aal.referrer_user_id,
                u.username AS referrer_username,
                aal.event_type,
                aal.reason,
                aal.severity,
                aal.metadata,
                aal.created_at
            FROM affiliate_abuse_logs aal
            LEFT JOIN users u ON u.user_id = aal.referrer_user_id
            WHERE aal.user_id = %s
            ORDER BY aal.created_at DESC
        """,
            (user_id,),
        )
        return cur.fetchall()


# =========================
# 👤 Abuse Logs by Referrer
# =========================
def get_abuse_logs_by_referrer(referrer_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                aal.id,
                aal.user_id,
                u.username AS username,
                aal.event_type,
                aal.reason,
                aal.severity,
                aal.metadata,
                aal.created_at
            FROM affiliate_abuse_logs aal
            LEFT JOIN users u ON u.user_id = aal.user_id
            WHERE aal.referrer_user_id = %s
            ORDER BY aal.created_at DESC
        """,
            (referrer_user_id,),
        )
        return cur.fetchall()
