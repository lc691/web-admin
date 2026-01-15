from db.connect import get_db_cursor, get_dict_cursor


# ======================================================
# LIST VIP LOGS (ADMIN)
# ======================================================
def get_all_vip_logs():
    """
    Ambil semua log VIP beserta info user dan start_date dari vip_users.
    Mengembalikan list dict siap render di template.
    """
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT
                l.id,
                l.target_user_id,
                u.username,
                u.first_name,
                v.start_date,
                l.admin_user_id,
                l.paket,
                l.durasi_hari,
                l.expired_baru,
                l.keterangan,
                l.timestamp,
                l.source
            FROM vip_logs l
            LEFT JOIN users u ON u.user_id = l.target_user_id
            LEFT JOIN vip_users v ON v.user_id = l.target_user_id AND v.source_bot = 'drac1n'
            ORDER BY l.timestamp DESC
        """)
        logs = [dict(row) for row in cursor.fetchall()]

        # Hitung durasi rinci (hari, jam, menit)
        for log in logs:
            start = log.get("start_date")
            end = log.get("expired_baru")
            if start and end:
                delta = end - start
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                log["durasi_rinci"] = f"{days} hari {hours} jam {minutes} menit"
            else:
                log["durasi_rinci"] = "-"

        return logs


# ======================================================
# GET SINGLE LOG
# ======================================================
def get_log_by_id(log_id: int):
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                l.*,
                u.username,
                u.first_name
            FROM vip_logs l
            LEFT JOIN users u ON u.user_id = l.target_user_id
            WHERE l.id = %s
            LIMIT 1
            """,
            (log_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


# ======================================================
# UPDATE LOG (ADMIN ONLY)
# ======================================================
def update_vip_log(log_id: int, data: dict):
    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute(
            """
            UPDATE vip_logs
            SET
                paket = %s,
                durasi_hari = %s,
                expired_baru = %s,
                keterangan = %s
            WHERE id = %s
            """,
            (
                data["paket"],
                data["durasi_hari"],
                data["expired_baru"],
                data.get("keterangan"),
                log_id,
            ),
        )


# ======================================================
# DELETE LOG (ADMIN ONLY)
# ======================================================
def delete_vip_log(log_id: int):
    with get_db_cursor(commit=True) as (cursor, _):
        cursor.execute(
            "DELETE FROM vip_logs WHERE id = %s",
            (log_id,),
        )
