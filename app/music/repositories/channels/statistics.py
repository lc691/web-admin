"""
Channel Statistics Repository
"""

from psycopg2.extras import DictRow


class ChannelStatisticsRepository:
    """
    Repository untuk statistik Channel.
    """

    @staticmethod
    def summary(cursor) -> dict:
        cursor.execute("""
            SELECT
                COUNT(*)::INTEGER AS total_channels,

                COUNT(*) FILTER (
                    WHERE vermuk = TRUE
                )::INTEGER AS total_vermuk,

                COUNT(*) FILTER (
                    WHERE vermuk = FALSE
                )::INTEGER AS total_normal,

                (
                    SELECT COUNT(*)
                    FROM artists
                )::INTEGER AS total_artists,

                (
                    SELECT COUNT(*)
                    FROM songs
                )::INTEGER AS total_songs
            FROM channels
        """)

        row = cursor.fetchone()

        return dict(row)

    @staticmethod
    def total_channels(cursor) -> int:
        cursor.execute("""
            SELECT COUNT(*)
            FROM channels
        """)
        return cursor.fetchone()[0]

    @staticmethod
    def total_artists(cursor) -> int:
        cursor.execute("""
            SELECT COUNT(*)
            FROM artists
        """)
        return cursor.fetchone()[0]

    @staticmethod
    def total_songs(cursor) -> int:
        cursor.execute("""
            SELECT COUNT(*)
            FROM songs
        """)
        return cursor.fetchone()[0]

    @staticmethod
    def total_vermuk(cursor) -> int:
        cursor.execute("""
            SELECT COUNT(*)
            FROM channels
            WHERE vermuk = TRUE
        """)
        return cursor.fetchone()[0]

    @staticmethod
    def total_normal(cursor) -> int:
        cursor.execute("""
            SELECT COUNT(*)
            FROM channels
            WHERE vermuk = FALSE
        """)
        return cursor.fetchone()[0]