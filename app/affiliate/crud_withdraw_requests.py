# app/affiliate/crud_withdraw_requests.py

from db.connect import get_db_cursor, get_dict_cursor


# =====================================================
# GET PENDING WITHDRAW (ADMIN DASHBOARD)
# =====================================================
def get_pending_withdraws(limit: int = 50, offset: int = 0) -> list[dict]:
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT *
            FROM affiliate_withdraw_requests
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT %s OFFSET %I
        """,
            (limit, offset),
        )
        return cursor.fetchall()


# =====================================================
# GET WITHDRAW BY ID
# =====================================================
def get_withdraw_by_id(wd_id: int) -> dict | None:
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT *
            FROM affiliate_withdraw_requests
            WHERE id = %s
            LIMIT 1
        """,
            (wd_id,),
        )
        return cursor.fetchone()


# =====================================================
# GET WITHDRAW HISTORY PER USER
# =====================================================
def get_withdraw_history(user_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT *
            FROM affiliate_withdraw_requests
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """,
            (user_id, limit, offset),
        )
        return cursor.fetchall()


# =====================================================
# GET WITHDRAW BY STATUS (GLOBAL)
# =====================================================
def get_withdraws_by_status(
    status: str, limit: int = 50, offset: int = 0
) -> list[dict]:
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT *
            FROM affiliate_withdraw_requests
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """,
            (status, limit, offset),
        )
        return cursor.fetchall()


# =====================================================
# COUNT WITHDRAW (UNTUK PAGINATION)
# =====================================================
def count_withdraws(status: str | None = None) -> int:
    with get_dict_cursor() as (cursor, _):
        if status:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM affiliate_withdraw_requests
                WHERE status = %s
            """,
                (status,),
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM affiliate_withdraw_requests")

        return cursor.fetchone()["count"]


def approve_withdraw(wd_id: int, admin_id: int):
    with get_db_cursor(commit=True) as (cursor, _):

        # lock row
        cursor.execute(
            """
            SELECT user_id, amount, status
            FROM affiliate_withdraw_requests
            WHERE id = %s
            FOR UPDATE
        """,
            (wd_id,),
        )
        wd = cursor.fetchone()

        if not wd:
            raise ValueError("Withdraw tidak ditemukan")

        user_id, amount, status = wd

        if status != "pending":
            raise ValueError("Withdraw sudah diproses")

        # update withdraw status
        cursor.execute(
            """
            UPDATE affiliate_withdraw_requests
            SET status = 'approved',
                approved_by = %s,
                approved_at = NOW()
            WHERE id = %s
        """,
            (admin_id, wd_id),
        )

        # potong saldo affiliate user
        cursor.execute(
            """
            UPDATE users
            SET affiliate_balance = affiliate_balance - %s
            WHERE user_id = %s
        """,
            (amount, user_id),
        )

        return user_id, amount


def reject_withdraw(wd_id: int, admin_id: int, reason: str):
    with get_db_cursor(commit=True) as (cursor, _):

        cursor.execute(
            """
            SELECT status
            FROM affiliate_withdraw_requests
            WHERE id = %s
            FOR UPDATE
        """,
            (wd_id,),
        )
        wd = cursor.fetchone()

        if not wd:
            raise ValueError("Withdraw tidak ditemukan")

        if wd[0] != "pending":
            raise ValueError("Withdraw sudah diproses")

        cursor.execute(
            """
            UPDATE affiliate_withdraw_requests
            SET status = 'rejected',
                rejected_by = %s,
                rejected_at = NOW(),
                reject_reason = %s
            WHERE id = %s
        """,
            (admin_id, reason, wd_id),
        )
