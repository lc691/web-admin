"""
Songs Search Repository
=======================

Repository untuk pencarian dan DataTables.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from typing import Any

from app.core.database import get_dict_cursor

from .types import (
    SongFilters,
    SongListResult,
    SongRow,
)

# ==========================================================
# BUILD WHERE
# ==========================================================


def build_search_query(
    filters: SongFilters,
) -> tuple[str, list[Any]]:
    """
    Build WHERE clause.
    """

    where: list[str] = []
    params: list[Any] = []

    keyword = filters.get("keyword")

    if keyword:
        where.append(
            """
            (
                s.title ILIKE %s
                OR a.name ILIKE %s
                OR c.name ILIKE %s
            )
            """
        )

        like = f"%{keyword}%"

        params.extend(
            (
                like,
                like,
                like,
            )
        )

    if filters.get("channel_id") is not None:
        where.append("c.id = %s")
        params.append(filters["channel_id"])

    if filters.get("artist_id") is not None:
        where.append("a.id = %s")
        params.append(filters["artist_id"])

    if filters.get("status") is not None:
        where.append("s.status = %s")
        params.append(filters["status"])

    if not where:
        return "", params

    return "WHERE " + " AND ".join(where), params


# ==========================================================
# SEARCH SONGS
# ==========================================================


def search_songs(
    *,
    filters: SongFilters,
    start: int,
    length: int,
    order_by: str = "s.id",
    descending: bool = True,
) -> SongListResult:
    """
    Search songs.
    """

    where_sql, params = build_search_query(
        filters,
    )

    direction = "DESC" if descending else "ASC"

    sql = f"""
        SELECT
            s.id,
            s.title,

            a.id AS artist_id,
            a.name AS artist,

            c.id AS channel_id,
            c.name AS channel,

            s.status,
            s.release_date

        FROM songs s

        JOIN artists a
            ON s.artist_id = a.id

        JOIN channels c
            ON a.channel_id = c.id

        {where_sql}

        ORDER BY
            {order_by} {direction}

        LIMIT %s
        OFFSET %s
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            sql,
            [
                *params,
                length,
                start,
            ],
        )

        songs: list[SongRow] = cursor.fetchall()

    return {
        "total": count_total(),
        "filtered": count_filtered(filters),
        "songs": songs,
    }


# ==========================================================
# COUNT TOTAL
# ==========================================================


def count_total() -> int:
    """
    Count all songs.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM songs
            """
        )

        return cursor.fetchone()["total"]


# ==========================================================
# COUNT FILTERED
# ==========================================================


def count_filtered(
    filters: SongFilters,
) -> int:
    """
    Count filtered songs.
    """

    where_sql, params = build_search_query(
        filters,
    )

    print("WHERE :", where_sql)
    print("PARAMS:", params)

    sql = f"""
        SELECT
            COUNT(*) AS total

        FROM songs s

        JOIN artists a
            ON s.artist_id = a.id

        JOIN channels c
            ON a.channel_id = c.id

        {where_sql}
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            sql,
            params,
        )

        return cursor.fetchone()["total"]
