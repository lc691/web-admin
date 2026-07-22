"""
Artist Presenter
"""

from app.music.services.artists.service import ArtistService


class ArtistPresenter:
    """
    Presenter Artist.
    """

    # =====================================================
    # PAGE
    # =====================================================

    @staticmethod
    def list():
        """
        Data halaman artist.
        """

        channels = ArtistService.get_channels()
        statistics = ArtistService.statistics()

        return {
            "title": "Artists",
            "channels": channels,
            "statistics": statistics,
        }

    # =====================================================
    # DETAIL
    # =====================================================

    @staticmethod
    def detail(
        artist_id: int,
    ):
        """
        Detail artist.
        """

        artist = ArtistService.get_detail(
            artist_id,
        )

        statistics = {
            "total_songs": ArtistService.total_songs(
                artist_id,
            ),
            "song_status": ArtistService.song_status(
                artist_id,
            ),
        }

        return {
            "title": artist["name"],
            "artist": artist,
            "statistics": statistics,
        }

    # =====================================================
    # FORM CREATE
    # =====================================================

    @staticmethod
    def create():
        """
        Data form create.
        """

        return {
            "title": "Tambah Artist",
            "channels": ArtistService.get_channels(),
        }

    # =====================================================
    # FORM EDIT
    # =====================================================

    @staticmethod
    def edit(
        artist_id: int,
    ):
        """
        Data form edit.
        """

        return {
            "title": "Edit Artist",
            "artist": ArtistService.get_detail(
                artist_id,
            ),
            "channels": ArtistService.get_channels(),
        }

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def statistics():
        """
        Statistik artist.
        """

        return ArtistService.statistics()
