from db.connect import get_dict_cursor


def get_all_vip_logs():
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT l.id,l.target_user_id,u.username,l.admin_user_id,
                   l.paket,l.durasi_hari,l.expired_baru,l.keterangan,
                   l.timestamp,l.source
            FROM vip_logs l
            LEFT JOIN vip_users u ON l.target_user_id = u.user_id
            ORDER BY l.timestamp DESC
        """
        )
        return cursor.fetchall()


def get_log_by_id(log_id: int):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM vip_logs WHERE id=%s", (log_id,))
        return cursor.fetchone()


def update_vip_log(log_id: int, data: dict):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE vip_logs
            SET target_user_id=%s, paket=%s, durasi_hari=%s,
                expired_baru=%s, keterangan=%s
            WHERE id=%s
        """,
            (
                data["target_user_id"],
                data["paket"],
                data["durasi_hari"],
                data["expired_baru"],
                data.get("keterangan"),
                log_id,
            ),
        )
        conn.commit()


def delete_vip_log(log_id: int):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("DELETE FROM vip_logs WHERE id=%s", (log_id,))
        conn.commit()
