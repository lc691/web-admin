from db.connect import get_db_cursor


def get_affiliate_leaderboard(limit: int = 20):
    """
    Leaderboard affiliate berdasarkan total komisi
    """

    with get_db_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                referrer_user_id,
                COUNT(DISTINCT referred_user_id) AS total_referral,
                SUM(commission) AS total_commission,
                MAX(created_at) AS last_activity
            FROM affiliate_commission_logs
            GROUP BY referrer_user_id
            ORDER BY total_commission DESC
            LIMIT %s
        """,
            (limit,),
        )

        rows = cursor.fetchall()

    return [
        {
            "referrer_user_id": r[0],
            "total_referral": r[1],
            "total_commission": r[2],
            "last_activity": r[3],
        }
        for r in rows
    ]
