from db.connect import get_db_cursor


def list_payout_batches():
    with get_db_cursor() as (cur, _):
        cur.execute("""
            SELECT
                id,
                period_start,
                period_end,
                total_amount,
                total_affiliate,
                status,
                created_at,
                paid_at
            FROM affiliate_payout_batches
            ORDER BY created_at DESC
        """)
        return cur.fetchall()


def get_payout_batch(batch_id: int):
    with get_db_cursor() as (cur, _):
        cur.execute(
            """
            SELECT *
            FROM affiliate_payout_batches
            WHERE id=%s
        """,
            (batch_id,),
        )
        return cur.fetchone()


def get_payout_details(batch_id: int):
    with get_db_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                referrer_user_id,
                SUM(commission) AS total_commission,
                COUNT(*) AS total_tx
            FROM affiliate_commission_logs
            WHERE payout_batch_id=%s
            GROUP BY referrer_user_id
            ORDER BY total_commission DESC
        """,
            (batch_id,),
        )
        return cur.fetchall()


def mark_batch_paid(batch_id: int, admin_id: int):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute(
            """
            UPDATE affiliate_commission_logs
            SET payout_status='paid'
            WHERE payout_batch_id=%s
        """,
            (batch_id,),
        )

        cur.execute(
            """
            UPDATE affiliate_payout_batches
            SET status='paid',
                paid_by=%s,
                paid_at=NOW()
            WHERE id=%s
        """,
            (admin_id, batch_id),
        )
