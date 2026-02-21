from db.connect import get_dict_cursor


def list_files():
    with get_dict_cursor() as (cur, _):
        cur.execute("""
            SELECT
                f.id,
                f.file_name,
                f.file_type,
                f.is_paid,
                f.main_title,
                f.show_id,
                COUNT(sf.id) AS show_count
            FROM files f
            LEFT JOIN show_files sf ON sf.file_id = f.id
            GROUP BY f.id
            ORDER BY f.id DESC
            """)
        return cur.fetchall()


def get_file(file_id: int):
    with get_dict_cursor() as (cur, _):
        cur.execute(
            """
            SELECT
                f.*,
                COUNT(sf.id) AS show_count
            FROM files f
            LEFT JOIN show_files sf ON sf.file_id = f.id
            WHERE f.id = %s
            GROUP BY f.id
            """,
            (file_id,),
        )
        return cur.fetchone()


def update_file(file_id: int, data: dict):
    if not data:
        return

    with get_dict_cursor() as (cur, conn):

        # ========================
        # Ambil show_id lama
        # ========================
        cur.execute(
            "SELECT show_id FROM files WHERE id = %s",
            (file_id,),
        )
        row = cur.fetchone()
        if not row:
            return

        old_show_id = row["show_id"]

        # ========================
        # UPDATE files
        # ========================
        fields = []
        values = []

        for key, value in data.items():
            fields.append(f"{key} = %s")
            values.append(value)

        values.append(file_id)

        query = f"""
            UPDATE files
            SET {", ".join(fields)}
            WHERE id = %s
        """

        cur.execute(query, tuple(values))

        # ========================
        # SYNC show_files (hanya jika show_id diupdate)
        # ========================
        if "show_id" in data:
            new_show_id = data.get("show_id")

            # Jika tidak berubah → skip total
            if old_show_id == new_show_id:
                conn.commit()
                return

            # Jika sebelumnya ada relasi → hapus
            if old_show_id is not None:
                cur.execute(
                    """
                    DELETE FROM show_files
                    WHERE file_id = %s
                      AND show_id = %s
                    """,
                    (file_id, old_show_id),
                )

            # Jika ada show baru → insert
            if new_show_id is not None:
                cur.execute(
                    """
                    INSERT INTO show_files (show_id, file_id, message_id)
                    SELECT show_id, id, message_id
                    FROM files
                    WHERE id = %s
                    ON CONFLICT (show_id, file_id) DO NOTHING
                    """,
                    (file_id,),
                )

        conn.commit()


def get_file_usage_count(file_id: int) -> int:
    with get_dict_cursor() as (cur, _):
        cur.execute(
            "SELECT COUNT(*) FROM show_files WHERE file_id = %s",
            (file_id,),
        )
        return cur.fetchone()["count"]


def delete_file(file_id: int):
    with get_dict_cursor() as (cur, conn):
        cur.execute(
            "DELETE FROM files WHERE id = %s",
            (file_id,),
        )
        conn.commit()


def sync_show_files_by_show_id(show_id: int) -> int:
    """
    Sinkronkan semua file yang punya files.show_id = show_id
    ke tabel show_files.

    - Insert relasi jika belum ada
    - Isi files.main_title dari shows.title (prefix 🎬) jika kosong
    - Isi alias_name jika kosong
    """

    with get_dict_cursor() as (cur, conn):

        # =========================
        # Validasi show ada
        # =========================
        cur.execute(
            "SELECT title FROM shows WHERE id = %s",
            (show_id,),
        )
        row = cur.fetchone()
        if not row:
            return -1

        show_title = row["title"]

        # =========================
        # 1️⃣ Insert relasi baru
        # =========================
        cur.execute(
            """
            INSERT INTO show_files (show_id, file_id, message_id, alias_name)
            SELECT 
                f.show_id,
                f.id,
                f.message_id,
                f.main_title
            FROM files f
            WHERE f.show_id = %s
            ON CONFLICT (show_id, file_id)
            DO NOTHING
            """,
            (show_id,),
        )

        inserted = cur.rowcount

        # =========================
        # 2️⃣ Isi files.main_title dari shows.title jika kosong
        # =========================
        cur.execute(
            """
            UPDATE files
            SET main_title = %s
            WHERE show_id = %s
              AND (main_title IS NULL OR main_title = '')
            """,
            (f"🎬 {show_title}", show_id),
        )

        # =========================
        # 3️⃣ Isi alias_name jika kosong
        # =========================
        cur.execute(
            """
            UPDATE show_files sf
            SET alias_name = f.main_title
            FROM files f
            WHERE sf.file_id = f.id
              AND sf.show_id = %s
              AND (sf.alias_name IS NULL OR sf.alias_name = '')
              AND f.main_title IS NOT NULL
            """,
            (show_id,),
        )

        conn.commit()

        return inserted
