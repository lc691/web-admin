from db.connect import get_dict_cursor


def get_all_referrals(limit=100, offset=0):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                r.id,
                r.referrer_user_id,
                COALESCE(u1.username, 'Unknown') AS referrer_username,
                r.referred_user_id,
                COALESCE(u2.username, 'Unknown') AS referred_username,
                r.created_at
            FROM referrals r
            LEFT JOIN users u1 ON u1.user_id = r.referrer_user_id
            LEFT JOIN users u2 ON u2.user_id = r.referred_user_id
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """,
            (limit, offset),
        )
        return cur.fetchall()


def get_referrals_by_referrer(referrer_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                r.id,
                r.referred_user_id,
                COALESCE(u.username, 'Unknown') AS referred_username,
                r.created_at
            FROM referrals r
            LEFT JOIN users u ON u.user_id = r.referred_user_id
            WHERE r.referrer_user_id = %s
            ORDER BY r.created_at DESC
        """,
            (referrer_user_id,),
        )
        return cur.fetchall()


def get_referrer_of_user(user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                r.id,
                r.referrer_user_id,
                COALESCE(u.username, 'Unknown') AS referrer_username,
                r.created_at
            FROM referrals r
            LEFT JOIN users u ON u.user_id = r.referrer_user_id
            WHERE r.referred_user_id = %s
            LIMIT 1
        """,
            (user_id,),
        )
        return cur.fetchone()


def get_referrer_summary():
    """
    Ringkasan referrer:
    - siapa referrer
    - total referral
    - last referral activity
    """
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                r.referrer_user_id,
                COALESCE(u.username, u.first_name, 'Unknown') AS referrer_name,
                COUNT(r.id) AS total_referrals,
                MAX(r.created_at) AS last_activity
            FROM referrals r
            JOIN users u ON u.user_id = r.referrer_user_id
            GROUP BY r.referrer_user_id, referrer_name
            ORDER BY total_referrals DESC, last_activity DESC
        """)
        return cur.fetchall()


def get_users_with_referrals():
    """
    Daftar user yang punya referrer:
    - user
    - referrer
    - waktu join via referral
    """
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                r.referred_user_id AS user_id,
                COALESCE(u2.username, u2.first_name, 'Unknown') AS username,

                r.referrer_user_id,
                COALESCE(u1.username, u1.first_name, 'Unknown') AS referrer_name,

                r.created_at
            FROM referrals r
            JOIN users u1 ON u1.user_id = r.referrer_user_id
            JOIN users u2 ON u2.user_id = r.referred_user_id
            ORDER BY r.created_at DESC
        """)
        return cur.fetchall()


# def get_users_with_referrals():
#     """
#     Ambil semua user yang memiliki referrer
#     """
#     with get_dict_cursor() as (cur, _):
#         cur.execute(
#             """
#             SELECT
#                 u.user_id,
#                 u.username,
#                 r.referrer_user_id,
#                 ref.username AS referrer_name,
#                 r.created_at
#             FROM referrals r
#             JOIN users u
#                 ON u.user_id = r.referred_user_id
#             JOIN users ref
#                 ON ref.user_id = r.referrer_user_id
#             ORDER BY r.created_at DESC
#         """
#         )
#         return cur.fetchall()
