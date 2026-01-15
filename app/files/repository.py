from typing import Dict, List, Optional

from db.connect import get_db_cursor, get_dict_cursor


class FileRepository:

    def list_all(self) -> List[Dict]:
        with get_dict_cursor() as (cur, _):
            cur.execute("SELECT * FROM files ORDER BY id DESC")
            return cur.fetchall()

    def get_by_id(self, file_id: int) -> Optional[Dict]:
        with get_dict_cursor() as (cur, _):
            cur.execute("SELECT * FROM files WHERE id=%s", (file_id,))
            return cur.fetchone()

    def list_all_with_show_files(self) -> List[Dict]:
        """
        List semua file beserta show_files terkait (jika ada)
        """
        with get_dict_cursor() as (cur, _):
            cur.execute(
                """
                SELECT 
                    f.*, 
                    sf.id AS show_file_id,
                    sf.show_id,
                    sf.message_id AS show_file_message_id,
                    sf.alias_name
                FROM files f
                LEFT JOIN show_files sf ON sf.file_id = f.id
                ORDER BY f.id DESC
            """
            )
            return cur.fetchall()

    def get_by_id_with_show_files(self, file_id: int) -> Optional[Dict]:
        """
        Ambil file berdasarkan id beserta show_files terkait (jika ada)
        """
        with get_dict_cursor() as (cur, _):
            cur.execute(
                """
                SELECT 
                    f.*, 
                    sf.id AS show_file_id,
                    sf.show_id,
                    sf.message_id AS show_file_message_id,
                    sf.alias_name
                FROM files f
                LEFT JOIN show_files sf ON sf.file_id = f.id
                WHERE f.id = %s
            """,
                (file_id,),
            )
            return cur.fetchone()

    def insert(
        self,
        file_id: str,
        file_name: str,
        free_hash: str,
        paid_hash: str,
        channel_username: str,
        file_type: str,
        file_size: int,
        message_id: int,
        main_title: Optional[str] = None,
        show_id: Optional[int] = None,
    ) -> int:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(
                """
                INSERT INTO files (
                    file_id, file_name, free_hash, paid_hash,
                    channel_username, file_type, file_size,
                    message_id, main_title, show_id
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """,
                (
                    file_id,
                    file_name,
                    free_hash,
                    paid_hash,
                    channel_username,
                    file_type,
                    file_size,
                    message_id,
                    main_title,
                    show_id,
                ),
            )
            return cur.fetchone()[0]

    def update(
        self,
        id: int,
        file_name: str,
        channel_username: str,
        file_type: str,
        main_title: str,
        show_id: Optional[int],
    ) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(
                """
                UPDATE files SET
                    file_name=%s,
                    channel_username=%s,
                    file_type=%s,
                    main_title=%s,
                    show_id=%s
                WHERE id=%s
            """,
                (
                    file_name,
                    channel_username,
                    file_type,
                    main_title,
                    show_id,
                    id,
                ),
            )

    def update_full(
        self,
        file_id: int,
        file_name: str,
        file_type: str,
        file_size: int,
        main_title: str,
        channel_username: str,
        is_paid: bool,  # ⬅️ TAMBAHAN
        message_id: Optional[int],
        show_id: Optional[int],
    ) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(
                """
                UPDATE files SET
                    file_name=%s,
                    file_type=%s,
                    file_size=%s,
                    main_title=%s,
                    channel_username=%s,
                    is_paid=%s,
                    message_id=%s,
                    show_id=%s
                WHERE id=%s
            """,
                (
                    file_name,
                    file_type,
                    file_size,
                    main_title,
                    channel_username,
                    is_paid,
                    message_id,
                    show_id,
                    file_id,
                ),
            )

    def delete(self, file_id: int) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("DELETE FROM files WHERE id=%s", (file_id,))
