class ChannelStatisticsRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    # =====================================================
    # OVERVIEW
    # =====================================================

    def overview(self):
        self.cursor.execute(
            """
            SELECT
                COUNT(*) AS total_channels,
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(s.id) AS total_songs,
                COUNT(CASE WHEN s.status = 'Live' THEN 1 END) AS live_songs,
                COUNT(CASE WHEN s.status = 'Approved' THEN 1 END) AS approved_songs,
                COUNT(CASE WHEN s.status = 'Review' THEN 1 END) AS review_songs,
                COUNT(CASE WHEN s.status = 'Take Down' THEN 1 END) AS takedown_songs,
                COUNT(CASE WHEN s.status = 'Topic' THEN 1 END) AS topic_songs
            FROM channels c
            LEFT JOIN artists a
                ON a.channel_id = c.id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            """
        )

        return self.cursor.fetchone()

    # =====================================================
    # CHANNEL SUMMARY
    # =====================================================

    def summary(self, channel_id: int):
        self.cursor.execute(
            """
            SELECT
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(s.id) AS total_songs,
                COUNT(CASE WHEN s.status = 'Live' THEN 1 END) AS live_songs,
                COUNT(CASE WHEN s.status = 'Approved' THEN 1 END) AS approved_songs,
                COUNT(CASE WHEN s.status = 'Review' THEN 1 END) AS review_songs,
                COUNT(CASE WHEN s.status = 'Take Down' THEN 1 END) AS takedown_songs,
                COUNT(CASE WHEN s.status = 'Topic' THEN 1 END) AS topic_songs
            FROM channels c
            LEFT JOIN artists a
                ON a.channel_id = c.id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE c.id = %s
            """,
            (channel_id,),
        )

        return self.cursor.fetchone()

    # =====================================================
    # STATUS DISTRIBUTION
    # =====================================================

    def status_distribution(self, channel_id: int):
        self.cursor.execute(
            """
            SELECT
                s.status,
                COUNT(*) AS total
            FROM songs s
            JOIN artists a
                ON a.id = s.artist_id
            WHERE a.channel_id = %s
            GROUP BY s.status
            ORDER BY s.status
            """,
            (channel_id,),
        )

        return self.cursor.fetchall()

    # =====================================================
    # TOP CHANNELS
    # =====================================================

    def top_channels(self, limit: int = 10):
        self.cursor.execute(
            """
            SELECT
                c.id,
                c.name,
                COUNT(s.id) AS total_songs
            FROM channels c
            LEFT JOIN artists a
                ON a.channel_id = c.id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            GROUP BY
                c.id,
                c.name
            ORDER BY total_songs DESC, c.name
            LIMIT %s
            """,
            (limit,),
        )

        return self.cursor.fetchall()