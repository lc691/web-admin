from db.connect import get_dict_cursor


def get_all_referrals():
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                r.id,
                r.referrer_user_id,
                u1.username AS referrer_username,
                r.referred_user_id,
                u2.username AS referred_username,
                r.created_at
            FROM referrals r
            JOIN users u1 ON u1.user_id = r.referrer_user_id
            JOIN users u2 ON u2.user_id = r.referred_user_id
            ORDER BY r.created_at DESC
        """)
        return cur.fetchall()


def get_referrals_by_referrer(referrer_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                r.id,
                r.referred_user_id,
                u.username AS referred_username,
                r.created_at
            FROM referrals r
            JOIN users u ON u.user_id = r.referred_user_id
            WHERE r.referrer_user_id = %s
            ORDER BY r.created_at DESC
        """, (referrer_user_id,))
        return cur.fetchall()


def get_referral_of_user(user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                r.id,
                r.referrer_user_id,
                u.username AS referrer_username,
                r.created_at
            FROM referrals r
            JOIN users u ON u.user_id = r.referrer_user_id
            WHERE r.referred_user_id = %s
        """, (user_id,))
        return cur.fetchone()
