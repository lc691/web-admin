from db.connect import get_dict_cursor


def get_all_referral_metrics(limit: int = 500):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                m.referrer_user_id,
                u.username AS referrer_username,
                m.window_start,
                m.count
            FROM referral_metrics m
            JOIN users u ON u.user_id = m.referrer_user_id
            ORDER BY m.window_start DESC, m.count DESC
            LIMIT %s
        """,
            (limit,),
        )
        return cur.fetchall()


def get_metrics_by_referrer(referrer_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                window_start,
                count
            FROM referral_metrics
            WHERE referrer_user_id = %s
            ORDER BY window_start DESC
        """,
            (referrer_user_id,),
        )
        return cur.fetchall()
