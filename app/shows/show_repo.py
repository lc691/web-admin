from typing import Optional, Dict, List
from db.connect import get_db_cursor, get_dict_cursor


class ShowRepository:
    def list_all(self) -> List[Dict]:
        with get_dict_cursor() as (cur, _):
            cur.execute("""
                SELECT id, title, thumbnail_url, sinopsis,
                       genre, hashtags, source, is_adult
                FROM shows
                ORDER BY id DESC
            """)
            return cur.fetchall()

    def get_by_id(self, show_id: int) -> Optional[Dict]:
        with get_dict_cursor() as (cur, _):
            cur.execute("SELECT * FROM shows WHERE id=%s", (show_id,))
            return cur.fetchone()

    def insert(self, data: Dict) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("""
                INSERT INTO shows (
                    title, sinopsis, genre, hashtags,
                    source, thumbnail_url, is_adult, posted_at
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
            """, (
                data["title"],
                data.get("sinopsis"),
                data.get("genre"),
                data.get("hashtags"),
                data.get("source"),
                data.get("thumbnail_url"),
                data.get("is_adult", False),
            ))

    def update(self, show_id: int, data: Dict) -> None:
        fields, values = [], []
        for k, v in data.items():
            fields.append(f"{k}=%s")
            values.append(v)

        if not fields:
            return

        values.append(show_id)
        q = f"UPDATE shows SET {', '.join(fields)} WHERE id=%s"

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(q, tuple(values))

    def delete(self, show_id: int) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("DELETE FROM shows WHERE id=%s", (show_id,))
