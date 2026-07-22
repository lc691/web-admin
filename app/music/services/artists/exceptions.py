"""
Artist Exceptions
"""


class ArtistException(Exception):
    """
    Base Exception Artist.
    """

    default_message = "Terjadi kesalahan pada Artist."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


# =====================================================
# NOT FOUND
# =====================================================

class ArtistNotFoundError(ArtistException):
    default_message = "Artist tidak ditemukan."


class ChannelNotFoundError(ArtistException):
    default_message = "Channel tidak ditemukan."


# =====================================================
# DUPLICATE
# =====================================================

class ArtistAlreadyExistsError(ArtistException):
    default_message = "Artist sudah ada."


# =====================================================
# VALIDATION
# =====================================================

class InvalidArtistNameError(ArtistException):
    default_message = "Nama artist tidak valid."


class InvalidChannelError(ArtistException):
    default_message = "Channel tidak valid."


# =====================================================
# DELETE
# =====================================================

class ArtistHasSongsError(ArtistException):
    default_message = (
        "Artist tidak dapat dihapus karena masih memiliki lagu."
    )


class ArtistDeleteError(ArtistException):
    default_message = "Gagal menghapus artist."


# =====================================================
# BULK
# =====================================================

class BulkDeleteError(ArtistException):
    default_message = "Bulk delete artist gagal."


class EmptySelectionError(ArtistException):
    default_message = "Tidak ada artist yang dipilih."


# =====================================================
# DATABASE
# =====================================================

class ArtistDatabaseError(ArtistException):
    default_message = "Terjadi kesalahan database."