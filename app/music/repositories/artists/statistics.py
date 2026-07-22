"""
Artist Statistics Repository
"""


class ArtistStatisticsRepository:
    """
    Repository statistik Artist.
    """

    # =====================================================
    # DASHBOARD
    # =====================================================

    @staticmethod
    def statistics(cursor, channel_id: int | None = None):
        """
        Statistik Artist.
        """

        sql = """
            SELECT
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(DISTINCT s.id) AS total_songs,
                COUNT(DISTINCT c.id) AS active_channels
            FROM artists a
            INNER JOIN channels c
                ON c.id = a.channel_id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE TRUE
        """

        params = []

        if channel_id is not None:
            sql += """
                AND a.channel_id = %s
            """
            params.append(channel_id)

        cursor.execute(sql, params)

        row = cursor.fetchone()

        return {
            "total_artists": row["total_artists"] or 0,
            "total_songs": row["total_songs"] or 0,
            "active_channels": row["active_channels"] or 0,
        }

    # =====================================================
    # TOTAL ARTISTS
    # =====================================================

    @staticmethod
    def total_artists(cursor, channel_id: int | None = None):
        sql = """
            SELECT
                COUNT(*) AS total
            FROM artists
            WHERE TRUE
        """

        params = []

        if channel_id is not None:
            sql += """
                AND channel_id = %s
            """
            params.append(channel_id)

        cursor.execute(sql, params)

        return cursor.fetchone()["total"]

    # =====================================================
    # TOTAL SONGS
    # =====================================================

    @staticmethod
    def total_songs(cursor, artist_id: int):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM songs
            WHERE artist_id = %s
            """,
            (artist_id,),
        )

        return cursor.fetchone()["total"]

    # =====================================================
    # ACTIVE CHANNELS
    # =====================================================

    @staticmethod
    def active_channels(cursor):
        """
        Jumlah channel yang memiliki minimal satu artist.
        """

        cursor.execute(
            """
            SELECT
                COUNT(DISTINCT channel_id) AS total
            FROM artists
            """
        )

        return cursor.fetchone()["total"]

    # =====================================================
    # SONG STATUS
    # =====================================================

    @staticmethod
    def song_status(cursor, artist_id: int):
        """
        Statistik status lagu per artist.
        """

        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS total
            FROM songs
            WHERE artist_id = %s
            GROUP BY status
            ORDER BY status
            """,
            (artist_id,),
        )

        return cursor.fetchall()

    # =====================================================
    # CHANNEL SUMMARY
    # =====================================================

    @staticmethod
    def channel_summary(cursor, channel_id: int):
        """
        Ringkasan artist dalam satu channel.
        """

        cursor.execute(
            """
            SELECT
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(DISTINCT s.id) AS total_songs
            FROM artists a
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE a.channel_id = %s
            """,
            (channel_id,),
        )

        return cursor.fetchone()