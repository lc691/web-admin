from db.connect import get_dict_cursor


# =========================
# 📋 Semua Transaksi Affiliate
# =========================
def get_all_transactions():
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                at.id,
                at.referrer_user_id,
                u1.username AS referrer_username,

                at.referred_user_id,
                u2.username AS referred_username,

                at.vip_package_name,
                at.vip_price,
                at.commission_amount,
                at.created_at
            FROM affiliate_transactions at
            JOIN users u1 ON u1.user_id = at.referrer_user_id
            JOIN users u2 ON u2.user_id = at.referred_user_id
            ORDER BY at.created_at DESC
        """)
        return cur.fetchall()


# =========================
# 👤 Transaksi by Referrer
# =========================
def get_transactions_by_referrer(referrer_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                at.id,
                at.referred_user_id,
                u.username AS referred_username,

                at.vip_package_name,
                at.vip_price,
                at.commission_amount,
                at.created_at
            FROM affiliate_transactions at
            JOIN users u ON u.user_id = at.referred_user_id
            WHERE at.referrer_user_id = %s
            ORDER BY at.created_at DESC
        """, (referrer_user_id,))
        return cur.fetchall()


# =========================
# 👥 Transaksi by Referred User
# =========================
def get_transactions_by_referred_user(referred_user_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                at.id,
                at.referrer_user_id,
                u.username AS referrer_username,

                at.vip_package_name,
                at.vip_price,
                at.commission_amount,
                at.created_at
            FROM affiliate_transactions at
            JOIN users u ON u.user_id = at.referrer_user_id
            WHERE at.referred_user_id = %s
            ORDER BY at.created_at DESC
        """, (referred_user_id,))
        return cur.fetchall()


# =========================
# 💎 Transaksi by VIP Package
# =========================
def get_transactions_by_package(vip_package_name: str):
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                at.id,
                at.referrer_user_id,
                u1.username AS referrer_username,

                at.referred_user_id,
                u2.username AS referred_username,

                at.vip_price,
                at.commission_amount,
                at.created_at
            FROM affiliate_transactions at
            JOIN users u1 ON u1.user_id = at.referrer_user_id
            JOIN users u2 ON u2.user_id = at.referred_user_id
            WHERE at.vip_package_name = %s
            ORDER BY at.created_at DESC
        """, (vip_package_name,))
        return cur.fetchall()


# =========================
# ➕ Create Transaction
# =========================
def create_affiliate_transaction(
    referrer_user_id: int,
    referred_user_id: int,
    vip_package_name: str,
    vip_price: int,
    commission_amount: int,
):
    with get_dict_cursor() as (cur, conn):
        cur.execute("""
            INSERT INTO affiliate_transactions (
                referrer_user_id,
                referred_user_id,
                vip_package_name,
                vip_price,
                commission_amount
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            referrer_user_id,
            referred_user_id,
            vip_package_name,
            vip_price,
            commission_amount
        ))

        transaction_id = cur.fetchone()["id"]
        conn.commit()
        return transaction_id


# =========================
# ❌ Delete Transaction
# =========================
def delete_transaction(transaction_id: int):
    with get_dict_cursor() as (cur, conn):
        cur.execute("""
            DELETE FROM affiliate_transactions
            WHERE id = %s
            RETURNING id
        """, (transaction_id,))

        deleted = cur.fetchone()
        conn.commit()
        return bool(deleted)
