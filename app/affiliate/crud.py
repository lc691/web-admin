from db.connect import get_dict_cursor

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def _paginate(page: int, limit: int):
    page = max(page, 1)
    limit = min(max(limit, 1), MAX_LIMIT)
    return limit, (page - 1) * limit


def get_all_transactions(page=1, limit=DEFAULT_LIMIT):
    limit, offset = _paginate(page, limit)

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                id,
                referrer_user_id,
                referred_user_id,
                paket,
                price,
                commission,
                created_at,
                notes
            FROM affiliate_commission_logs
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """,
            (limit, offset),
        )

        items = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM affiliate_commission_logs")
        total = cursor.fetchone()["count"]

    return {"items": items, "page": page, "limit": limit, "total": total}


def get_transactions_by_referrer(user_id: int):
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT *
            FROM affiliate_commission_logs
            WHERE referrer_user_id = %s
            ORDER BY created_at DESC
        """,
            (user_id,),
        )
        return cursor.fetchall()


def get_transactions_by_referred_user(user_id: int):
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT *
            FROM affiliate_commission_logs
            WHERE referred_user_id = %s
            ORDER BY created_at DESC
        """,
            (user_id,),
        )
        return cursor.fetchall()


def get_transactions_by_package(paket: str):
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT *
            FROM affiliate_commission_logs
            WHERE paket = %s
            ORDER BY created_at DESC
        """,
            (paket,),
        )
        return cursor.fetchall()
