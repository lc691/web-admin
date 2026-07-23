"""
Artist Mapper
"""


class ArtistMapper:
    """
    Mapper Artist.
    """

    # =====================================================
    # DATATABLE
    # =====================================================

    @staticmethod
    def to_datatable(row: dict) -> dict:
        """
        Format Artist untuk DataTables.
        """

        created_at = row.get("created_at")
        updated_at = row.get("updated_at")

        return {
            "id": row["id"],
            "channel_id": row["channel_id"],
            "channel_name": row.get("channel_name", "-"),
            "name": row["name"],
            "song_count": row.get("song_count", 0),
            "created_at": (
                created_at.strftime("%Y-%m-%d %H:%M")
                if created_at
                else None
            ),
            "updated_at": (
                updated_at.strftime("%Y-%m-%d %H:%M")
                if updated_at
                else None
            ),
        }

    # =====================================================
    # DETAIL
    # =====================================================

    @staticmethod
    def to_detail(row: dict) -> dict:

        created_at = row.get("created_at")
        updated_at = row.get("updated_at")

        return {
            "id": row["id"],
            "channel_id": row["channel_id"],
            "channel_name": row.get("channel_name"),
            "name": row["name"],
            "song_count": row.get("song_count", 0),
            "created_at": (
                created_at.strftime("%Y-%m-%d %H:%M")
                if created_at
                else None
            ),
            "updated_at": (
                updated_at.strftime("%Y-%m-%d %H:%M")
                if updated_at
                else None
            ),
        }

    # =====================================================
    # FORM
    # =====================================================

    @staticmethod
    def to_form(row: dict) -> dict:
        """
        Format untuk form edit.
        """

        return {
            "id": row["id"],
            "channel_id": row["channel_id"],
            "name": row["name"],
        }

    # =====================================================
    # RESPONSE
    # =====================================================

    @staticmethod
    def to_response(row: dict) -> dict:
        """
        JSON Response.
        """

        return {
            "id": row["id"],
            "channel_id": row["channel_id"],
            "channel_name": row.get("channel_name"),
            "name": row["name"],
            "song_count": row.get("song_count", 0),
        }

    # =====================================================
    # LIST
    # =====================================================

    @classmethod
    def to_list(cls, rows: list[dict]) -> list[dict]:
        """
        Mapping list artist.
        """

        return [
            cls.to_datatable(row)
            for row in rows
        ]

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def to_statistics(stats: dict) -> dict:
        """
        Mapping statistik artist.
        """

        return {
            "total_artists": stats.get("total_artists", 0),
            "total_songs": stats.get("total_songs", 0),
            "active_channels": stats.get("active_channels", 0),
        }

    # =====================================================
    # SELECT
    # =====================================================

    @staticmethod
    def to_select(rows: list[dict]) -> list[dict]:
        """
        Dropdown Artist.
        """

        return [
            {
                "id": row["id"],
                "name": row["name"],
            }
            for row in rows
        ]

    # =====================================================
    # CHANNELS
    # =====================================================

    @staticmethod
    def channels(rows: list[dict]) -> list[dict]:
        """
        Dropdown Channel.
        """

        return [
            {
                "id": row["id"],
                "name": row["name"],
            }
            for row in rows
        ]

    @staticmethod
    def channel(row):
        return row