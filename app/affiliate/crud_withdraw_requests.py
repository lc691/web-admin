from db.connect import get_dict_cursor


# =========================
# 📋 Semua Withdraw Requests
# =========================
def get_all_withdraw_requests():
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                awr.id,
                awr.user_id,
                u.username,
                awr.amount,
                awr.status,
                awr.note,
                awr.created_at,
                awr.updated_at
            FROM affiliate_withdraw_requests awr
            JOIN users u ON u.user_id = awr.user_id
            ORDER BY awr.created_at DESC
        """
        )
        return cur.fetchall()


# =========================
# ⏳ Withdraw Pending
# =========================
def get_pending_withdraw_requests():
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                awr.id,
                awr.user_id,
                u.username,
                awr.amount,
                awr.note,
                awr.created_at
            FROM affiliate_withdraw_requests awr
            JOIN users u ON u.user_id = awr.user_id
            WHERE awr.status = 'pending'
            ORDER BY awr.created_at ASC
        """
        )
        return cur.fetchall()


# =========================
# 👤 Withdraw by User
# =========================
def get_withdraw_requests_by_user(user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                id,
                amount,
                status,
                note,
                created_at,
                updated_at
            FROM affiliate_withdraw_requests
            WHERE user_id = %s
            ORDER BY created_at DESC
        """,
            (user_id,),
        )
        return cur.fetchall()


# =========================
# ➕ Create Withdraw Request
# =========================
def create_withdraw_request(user_id: int, amount: int, note: str | None = None):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            INSERT INTO affiliate_withdraw_requests (
                user_id,
                amount,
                note
            ) VALUES (%s, %s, %s)
            RETURNING id
        """,
            (user_id, amount, note),
        )

        wd_id = cur.fetchone()["id"]
        conn.commit()
        return wd_id


# =========================
# ✅ Update Withdraw Status
# =========================
def update_withdraw_status(
    withdraw_id: int,
    status: str,
    note: str | None = None,
):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            UPDATE affiliate_withdraw_requests
            SET
                status = %s,
                note = %s
            WHERE id = %s
            RETURNING id
        """,
            (status, note, withdraw_id),
        )

        updated = cur.fetchone()
        conn.commit()
        return bool(updated)


