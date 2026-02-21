from db.connect import get_dict_cursor


def get_all_referral_logs(limit: int = 500):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                l.id,
                l.referrer_user_id,
                u1.username AS referrer_username,
                l.referred_user_id,
                u2.username AS referred_username,
                l.event_type,
                l.created_at
            FROM referral_logs l
            LEFT JOIN users u1 ON u1.user_id = l.referrer_user_id
            LEFT JOIN users u2 ON u2.user_id = l.referred_user_id
            ORDER BY l.created_at DESC
            LIMIT %s
        """,
            (limit,),
        )
        return cur.fetchall()


def get_logs_by_referrer(referrer_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                l.id,
                l.referred_user_id,
                u.username AS referred_username,
                l.event_type,
                l.created_at
            FROM referral_logs l
            LEFT JOIN users u ON u.user_id = l.referred_user_id
            WHERE l.referrer_user_id = %s
            ORDER BY l.created_at DESC
        """,
            (referrer_user_id,),
        )
        return cur.fetchall()
