from db.connect import get_dict_cursor


# =========================
# 📋 Semua Log Komisi Affiliate
# =========================
def get_all_commission_logs():
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                acl.id,

                acl.referrer_user_id,
                u1.username AS referrer_username,

                acl.referred_user_id,
                u2.username AS referred_username,

                acl.paket,
                acl.price,
                acl.commission,
                acl.notes,
                acl.created_at
            FROM affiliate_commission_logs acl
            JOIN users u1 ON u1.user_id = acl.referrer_user_id
            JOIN users u2 ON u2.user_id = acl.referred_user_id
            ORDER BY acl.created_at DESC
        """
        )
        return cur.fetchall()


# =========================
# 👤 Log Komisi by Referrer
# =========================
def get_commission_logs_by_referrer(referrer_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                acl.id,

                acl.referred_user_id,
                u.username AS referred_username,

                acl.paket,
                acl.price,
                acl.commission,
                acl.notes,
                acl.created_at
            FROM affiliate_commission_logs acl
            JOIN users u ON u.user_id = acl.referred_user_id
            WHERE acl.referrer_user_id = %s
            ORDER BY acl.created_at DESC
        """,
            (referrer_user_id,),
        )
        return cur.fetchall()


# =========================
# 👥 Log Komisi by Referred User
# =========================
def get_commission_logs_by_referred(referred_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                acl.id,

                acl.referrer_user_id,
                u.username AS referrer_username,

                acl.paket,
                acl.price,
                acl.commission,
                acl.notes,
                acl.created_at
            FROM affiliate_commission_logs acl
            JOIN users u ON u.user_id = acl.referrer_user_id
            WHERE acl.referred_user_id = %s
            ORDER BY acl.created_at DESC
        """,
            (referred_user_id,),
        )
        return cur.fetchall()


# =========================
# ➕ Create Commission Log
# =========================
def create_commission_log(
    referrer_user_id: int,
    referred_user_id: int,
    paket: str,
    price: int,
    commission: int,
    notes: str | None = None,
):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            INSERT INTO affiliate_commission_logs (
                referrer_user_id,
                referred_user_id,
                paket,
                price,
                commission,
                notes
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """,
            (referrer_user_id, referred_user_id, paket, price, commission, notes),
        )

        log_id = cur.fetchone()["id"]
        conn.commit()
        return log_id


# =========================
# ❌ Delete Commission Log
# =========================
def delete_commission_log(log_id: int):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            """
            DELETE FROM affiliate_commission_logs
            WHERE id = %s
            RETURNING id
        """,
            (log_id,),
        )

        deleted = cur.fetchone()
        conn.commit()
        return bool(deleted)
