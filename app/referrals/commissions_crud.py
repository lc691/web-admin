from db.connect import get_dict_cursor


def get_all_commissions(limit: int = 500):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                c.id,
                c.upline_user_id,
                u1.username AS upline_username,
                c.downline_user_id,
                u2.username AS downline_username,
                c.paket_name,
                c.price,
                c.commission,
                c.created_at
            FROM referral_commissions c
            LEFT JOIN users u1 ON u1.user_id = c.upline_user_id
            LEFT JOIN users u2 ON u2.user_id = c.downline_user_id
            ORDER BY c.created_at DESC
            LIMIT %s
        """,
            (limit,),
        )
        return cur.fetchall()


def get_commissions_by_upline(upline_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                c.id,
                c.downline_user_id,
                u.username AS downline_username,
                c.paket_name,
                c.price,
                c.commission,
                c.created_at
            FROM referral_commissions c
            LEFT JOIN users u ON u.user_id = c.downline_user_id
            WHERE c.upline_user_id = %s
            ORDER BY c.created_at DESC
        """,
            (upline_user_id,),
        )
        return cur.fetchall()
