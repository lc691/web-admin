from typing import Dict, List, Optional

from db.connect import get_db_cursor, get_dict_cursor

ALLOWED_FIELDS = {
    "title",
    "sinopsis",
    "genre",
    "hashtags",
    "source_id",
    "thumbnail_url",
    "is_adult",
}


class ShowRepository:

    # =========================
    # LIST WITH SOURCE LABEL
    # =========================
    def list_all(self) -> List[Dict]:
        with get_dict_cursor() as (cur, _):
            cur.execute(
                """
                SELECT 
                    s.id,
                    s.title,
                    s.thumbnail_url,
                    s.sinopsis,
                    s.genre,
                    s.hashtags,
                    s.source_id,
                    r.label AS source_label,
                    s.is_adult
                FROM shows s
                JOIN request_sources r 
                    ON s.source_id = r.id
                ORDER BY s.id DESC
            """
            )
            return cur.fetchall()

    # =========================
    # GET SINGLE SHOW
    # =========================
    def get_by_id(self, show_id: int) -> Optional[Dict]:
        with get_dict_cursor() as (cur, _):
            cur.execute(
                """
                SELECT s.*, r.label AS source_label
                FROM shows s
                JOIN request_sources r
                    ON s.source_id = r.id
                WHERE s.id=%s
            """,
                (show_id,),
            )
            return cur.fetchone()

    # =========================
    # INSERT
    # =========================
    def insert(self, data: Dict) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(
                """
                INSERT INTO shows (
                    title,
                    sinopsis,
                    genre,
                    hashtags,
                    source_id,
                    thumbnail_url,
                    is_adult,
                    posted_at
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
                (
                    data["title"],
                    data.get("sinopsis"),
                    data.get("genre"),
                    data.get("hashtags"),
                    data.get("source_id"),
                    data.get("thumbnail_url"),
                    data.get("is_adult", False),
                ),
            )

    # =========================
    # UPDATE
    # =========================
    def update(self, show_id: int, data: Dict) -> None:
        ALLOWED_FIELDS = {
            "title",
            "sinopsis",
            "genre",
            "hashtags",
            "source_id",
            "thumbnail_url",
            "is_adult",
        }

        fields, values = [], []

        for k, v in data.items():
            if k in ALLOWED_FIELDS:
                fields.append(f"{k}=%s")
                values.append(v)

        if not fields:
            return

        values.append(show_id)

        q = f"UPDATE shows SET {', '.join(fields)} WHERE id=%s"

        with get_db_cursor(commit=True) as (cur, _):
            cur.execute(q, tuple(values))

    # =========================
    # DELETE
    # =========================
    def delete(self, show_id: int) -> None:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("DELETE FROM shows WHERE id=%s", (show_id,))
