from db.connect import get_db_cursor, get_dict_cursor


def get_all_channels() -> list[dict]:
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT id, nama_variabel, alias, nilai, keterangan, is_active FROM channel_admin ORDER BY id")
        return cur.fetchall()

def set_active_channel(channel_id: int):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE channel_admin SET is_active = FALSE")
        cur.execute("UPDATE channel_admin SET is_active = TRUE WHERE id = %s", (channel_id,))

def update_channel(channel_id: int, alias: str, keterangan: str):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE channel_admin SET alias = %s, keterangan = %s WHERE id = %s", (alias, keterangan, channel_id))
