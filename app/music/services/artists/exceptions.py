"""
Artist Exceptions - Complete Implementation

Exception hierarchy untuk semua error yang terkait dengan Artist operations.
Menggunakan inheritance untuk memudahkan error handling dan logging.
"""

from typing import Any, Dict, List, Optional


# =====================================================
# BASE EXCEPTION
# =====================================================

class ArtistException(Exception):
    """
    Base Exception Artist.
    """

    default_message = "Terjadi kesalahan pada Artist."

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None
    ):
        self.message = message or self.default_message
        self.details = details or {}
        self.code = code or self.__class__.__name__
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'details': self.details,
        }


# =====================================================
# NOT FOUND ERRORS
# =====================================================

class ArtistNotFoundError(ArtistException):
    """Artist tidak ditemukan."""
    default_message = "Artist tidak ditemukan."

    def __init__(
        self,
        artist_id: Optional[int] = None,
        name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if artist_id:
            message = f"Artist dengan ID '{artist_id}' tidak ditemukan"
            code = 'ARTIST_NOT_FOUND_BY_ID'
        elif name:
            message = f"Artist dengan nama '{name}' tidak ditemukan"
            code = 'ARTIST_NOT_FOUND_BY_NAME'
        else:
            message = self.default_message
            code = 'ARTIST_NOT_FOUND'

        details = details or {}
        if artist_id:
            details['artist_id'] = artist_id
        if name:
            details['name'] = name

        super().__init__(message, details, code)


class ArtistsNotFoundError(ArtistException):
    """Multiple artists tidak ditemukan."""
    default_message = "Beberapa artist tidak ditemukan."

    def __init__(
        self,
        artist_ids: List[int],
        not_found: List[int],
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{len(not_found)} dari {len(artist_ids)} artist tidak ditemukan"
        code = 'ARTISTS_NOT_FOUND'

        details = details or {}
        details['requested_ids'] = artist_ids
        details['not_found_ids'] = not_found
        details['found_count'] = len(artist_ids) - len(not_found)

        super().__init__(message, details, code)


class ChannelNotFoundError(ArtistException):
    """Channel tidak ditemukan."""
    default_message = "Channel tidak ditemukan."

    def __init__(
        self,
        channel_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if channel_id:
            message = f"Channel dengan ID '{channel_id}' tidak ditemukan"
            code = 'CHANNEL_NOT_FOUND'
        else:
            message = self.default_message
            code = 'CHANNEL_NOT_FOUND'

        details = details or {}
        if channel_id:
            details['channel_id'] = channel_id

        super().__init__(message, details, code)


# =====================================================
# DUPLICATE ERRORS
# =====================================================

class ArtistAlreadyExistsError(ArtistException):
    """Artist sudah ada di channel."""
    default_message = "Artist sudah ada."

    def __init__(
        self,
        name: Optional[str] = None,
        channel_id: Optional[int] = None,
        existing_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if name and channel_id:
            message = f"Artist '{name}' sudah ada di channel ini"
        elif name:
            message = f"Artist '{name}' sudah ada"
        else:
            message = self.default_message

        code = 'ARTIST_ALREADY_EXISTS'

        details = details or {}
        if name:
            details['name'] = name
        if channel_id:
            details['channel_id'] = channel_id
        if existing_id:
            details['existing_id'] = existing_id

        super().__init__(message, details, code)


class ArtistNameConflictError(ArtistException):
    """Konflik nama artist di channel yang sama."""
    default_message = "Nama artist sudah digunakan di channel ini."

    def __init__(
        self,
        name: str,
        channel_id: int,
        existing_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Artist '{name}' sudah ada di channel ID {channel_id}"
        code = 'ARTIST_NAME_CONFLICT'

        details = details or {}
        details['name'] = name
        details['channel_id'] = channel_id
        if existing_id:
            details['existing_id'] = existing_id

        super().__init__(message, details, code)


# =====================================================
# VALIDATION ERRORS
# =====================================================

class InvalidArtistNameError(ArtistException):
    """Nama artist tidak valid."""
    default_message = "Nama artist tidak valid."

    def __init__(
        self,
        name: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Nama artist '{name}' tidak valid: {reason}" if name else f"Nama artist tidak valid: {reason}"
        else:
            message = self.default_message

        code = 'INVALID_ARTIST_NAME'

        details = details or {}
        if name:
            details['name'] = name
        if reason:
            details['reason'] = reason

        super().__init__(message, details, code)


class InvalidChannelError(ArtistException):
    """Channel tidak valid."""
    default_message = "Channel tidak valid."

    def __init__(
        self,
        channel_id: Optional[int] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Channel ID {channel_id} tidak valid: {reason}" if channel_id else f"Channel tidak valid: {reason}"
        else:
            message = self.default_message

        code = 'INVALID_CHANNEL'

        details = details or {}
        if channel_id:
            details['channel_id'] = channel_id
        if reason:
            details['reason'] = reason

        super().__init__(message, details, code)


class InvalidArtistDataError(ArtistException):
    """Data artist tidak valid."""
    default_message = "Data artist tidak valid."

    def __init__(
        self,
        errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = "Data artist tidak valid. Periksa field yang salah."
        code = 'INVALID_ARTIST_DATA'

        details = details or {}
        if errors:
            details['errors'] = errors
            details['error_count'] = len(errors)

        super().__init__(message, details, code)

class InvalidArtistStatusError(ArtistException):
    """Status artist tidak valid."""
    default_message = "Status artist tidak valid."

    def __init__(
        self,
        status: Optional[str] = None,
        valid_statuses: Optional[list[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if status:
            message = f"Status artist '{status}' tidak valid."
        else:
            message = self.default_message

        code = "INVALID_ARTIST_STATUS"

        details = details or {}

        if status:
            details["status"] = status

        if valid_statuses:
            details["valid_statuses"] = valid_statuses

        super().__init__(message, details, code)

# =====================================================
# DELETE ERRORS
# =====================================================

class ArtistHasSongsError(ArtistException):
    """Artist tidak dapat dihapus karena masih memiliki lagu."""
    default_message = "Artist tidak dapat dihapus karena masih memiliki lagu."

    def __init__(
        self,
        artist_id: int,
        song_count: int,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Artist ID {artist_id} memiliki {song_count} lagu dan tidak dapat dihapus"
        code = 'ARTIST_HAS_SONGS'

        details = details or {}
        details['artist_id'] = artist_id
        details['song_count'] = song_count

        super().__init__(message, details, code)


class ArtistDeleteError(ArtistException):
    """Gagal menghapus artist."""
    default_message = "Gagal menghapus artist."

    def __init__(
        self,
        artist_id: Optional[int] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Gagal menghapus artist: {reason}"
        elif artist_id:
            message = f"Gagal menghapus artist ID {artist_id}"
        else:
            message = self.default_message

        code = 'ARTIST_DELETE_ERROR'

        details = details or {}
        if artist_id:
            details['artist_id'] = artist_id
        if reason:
            details['reason'] = reason

        super().__init__(message, details, code)


class ArtistDeleteWithSongsError(ArtistException):
    """Gagal menghapus artist dengan lagu."""
    default_message = "Tidak dapat menghapus artist yang memiliki lagu."

    def __init__(
        self,
        artist_ids: List[int],
        song_counts: Dict[int, int],
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{len(artist_ids)} artist tidak dapat dihapus karena memiliki lagu"
        code = 'ARTIST_DELETE_WITH_SONGS'

        details = details or {}
        details['artist_ids'] = artist_ids
        details['song_counts'] = song_counts
        details['total_songs'] = sum(song_counts.values())

        super().__init__(message, details, code)


# =====================================================
# BULK ERRORS
# =====================================================

class BulkDeleteError(ArtistException):
    """Bulk delete artist gagal."""
    default_message = "Bulk delete artist gagal."

    def __init__(
        self,
        failed_ids: Optional[List[int]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = "Bulk delete artist gagal"
        if failed_ids:
            message += f" untuk {len(failed_ids)} artist"

        code = 'BULK_DELETE_ERROR'

        details = details or {}
        if failed_ids:
            details['failed_ids'] = failed_ids
            details['failed_count'] = len(failed_ids)
        if errors:
            details['errors'] = errors
            details['error_count'] = len(errors)

        super().__init__(message, details, code)


class BulkUpdateError(ArtistException):
    """Bulk update artist gagal."""
    default_message = "Bulk update artist gagal."

    def __init__(
        self,
        failed_ids: Optional[List[int]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = "Bulk update artist gagal"
        if failed_ids:
            message += f" untuk {len(failed_ids)} artist"

        code = 'BULK_UPDATE_ERROR'

        details = details or {}
        if failed_ids:
            details['failed_ids'] = failed_ids
            details['failed_count'] = len(failed_ids)
        if errors:
            details['errors'] = errors
            details['error_count'] = len(errors)

        super().__init__(message, details, code)


class BulkInsertError(ArtistException):
    """Bulk insert artist gagal."""
    default_message = "Bulk insert artist gagal."

    def __init__(
        self,
        failed_items: Optional[List[Dict[str, Any]]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = "Bulk insert artist gagal"
        if failed_items:
            message += f" untuk {len(failed_items)} artist"

        code = 'BULK_INSERT_ERROR'

        details = details or {}
        if failed_items:
            details['failed_items'] = failed_items
            details['failed_count'] = len(failed_items)
        if errors:
            details['errors'] = errors
            details['error_count'] = len(errors)

        super().__init__(message, details, code)


class EmptySelectionError(ArtistException):
    """Tidak ada artist yang dipilih."""
    default_message = "Tidak ada artist yang dipilih."

    def __init__(
        self,
        details: Optional[Dict[str, Any]] = None
    ):
        message = "Tidak ada artist yang dipilih untuk operasi ini"
        code = 'EMPTY_SELECTION'

        super().__init__(message, details, code)


class BulkValidationError(ArtistException):
    """Validasi bulk artist gagal."""
    default_message = "Validasi bulk artist gagal."

    def __init__(
        self,
        validation_errors: Dict[int, List[str]],
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Validasi bulk artist gagal: {len(validation_errors)} error ditemukan"
        code = 'BULK_VALIDATION_ERROR'

        details = details or {}
        details['validation_errors'] = validation_errors
        details['error_count'] = len(validation_errors)

        super().__init__(message, details, code)


# =====================================================
# DATABASE ERRORS
# =====================================================

class ArtistDatabaseError(ArtistException):
    """Terjadi kesalahan database."""
    default_message = "Terjadi kesalahan database."

    def __init__(
        self,
        operation: Optional[str] = None,
        error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if operation:
            message = f"Kesalahan database saat {operation}"
        elif error:
            message = f"Kesalahan database: {error}"
        else:
            message = self.default_message

        code = 'ARTIST_DATABASE_ERROR'

        details = details or {}
        if operation:
            details['operation'] = operation
        if error:
            details['error'] = error

        super().__init__(message, details, code)


class ArtistConnectionError(ArtistException):
    """Error koneksi database."""
    default_message = "Gagal terhubung ke database."

    def __init__(
        self,
        details: Optional[Dict[str, Any]] = None
    ):
        message = "Gagal terhubung ke database untuk operasi artist"
        code = 'ARTIST_CONNECTION_ERROR'

        super().__init__(message, details, code)


class ArtistTransactionError(ArtistException):
    """Error transaksi database."""
    default_message = "Transaksi database gagal."

    def __init__(
        self,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if operation:
            message = f"Transaksi database gagal saat {operation}"
        else:
            message = self.default_message

        code = 'ARTIST_TRANSACTION_ERROR'

        details = details or {}
        if operation:
            details['operation'] = operation

        super().__init__(message, details, code)


# =====================================================
# FILTER / QUERY ERRORS
# =====================================================

class InvalidFilterError(ArtistException):
    """Filter tidak valid."""
    default_message = "Parameter filter tidak valid."

    def __init__(
        self,
        filter_param: str,
        filter_value: Any,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Filter '{filter_param}' tidak valid: {reason}"
        code = 'INVALID_FILTER'

        details = details or {}
        details['filter_param'] = filter_param
        details['filter_value'] = filter_value
        details['reason'] = reason

        super().__init__(message, details, code)


class InvalidSortError(ArtistException):
    """Sort tidak valid."""
    default_message = "Parameter sort tidak valid."

    def __init__(
        self,
        sort_column: str,
        sort_direction: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if sort_direction:
            message = f"Sort tidak valid: column '{sort_column}', direction '{sort_direction}'"
        else:
            message = f"Sort tidak valid: column '{sort_column}'"

        code = 'INVALID_SORT'

        details = details or {}
        details['sort_column'] = sort_column
        if sort_direction:
            details['sort_direction'] = sort_direction

        super().__init__(message, details, code)


# =====================================================
# PERMISSION ERRORS
# =====================================================

class ArtistPermissionError(ArtistException):
    """User tidak memiliki permission."""
    default_message = "Anda tidak memiliki izin untuk melakukan operasi ini."

    def __init__(
        self,
        action: str,
        artist_id: Optional[int] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Tidak memiliki izin untuk {action} artist"
        if artist_id:
            message += f" (ID: {artist_id})"

        code = 'ARTIST_PERMISSION_ERROR'

        details = details or {}
        details['action'] = action
        if artist_id:
            details['artist_id'] = artist_id
        if user_id:
            details['user_id'] = user_id

        super().__init__(message, details, code)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def create_artist_error_from_db_error(error: Exception) -> ArtistException:
    """
    Create appropriate artist exception from database error.
    
    Args:
        error: Database error
        
    Returns:
        ArtistException instance
    """
    error_message = str(error).lower()

    if 'duplicate key' in error_message:
        if 'name' in error_message:
            return ArtistAlreadyExistsError(
                details={'db_error': str(error)}
            )
        elif 'channel_id' in error_message:
            return InvalidChannelError(
                details={'db_error': str(error)}
            )
        else:
            return ArtistException(
                f"Duplicate record: {str(error)}",
                code='DB_DUPLICATE'
            )

    if 'not found' in error_message or 'does not exist' in error_message:
        return ArtistNotFoundError(
            details={'db_error': str(error)}
        )

    if 'connection' in error_message:
        return ArtistConnectionError(
            details={'db_error': str(error)}
        )

    if 'foreign key' in error_message:
        return ArtistHasSongsError(
            artist_id=0,
            song_count=0,
            details={'db_error': str(error)}
        )

    return ArtistDatabaseError(
        error=str(error),
        details={'db_error': str(error)}
    )


def create_bulk_error_from_results(
    action: str,
    total: int,
    success_count: int,
    failed_count: int
) -> Optional[ArtistException]:
    """
    Create bulk error if there were failures.
    
    Args:
        action: Action name (delete, update, insert)
        total: Total items processed
        success_count: Successful items
        failed_count: Failed items
        
    Returns:
        ArtistException if there were failures, None otherwise
    """
    if failed_count == 0:
        return None

    if action == 'delete':
        return BulkDeleteError(
            details={
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )
    elif action == 'update':
        return BulkUpdateError(
            details={
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )
    elif action == 'insert':
        return BulkInsertError(
            details={
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )
    else:
        return ArtistException(
            f"Bulk operation partially failed: {failed_count} of {total} failed",
            details={
                'action': action,
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    # Base
    'ArtistException',
    
    # Not Found
    'ArtistNotFoundError',
    'ArtistsNotFoundError',
    'ChannelNotFoundError',
    
    # Duplicate
    'ArtistAlreadyExistsError',
    'ArtistNameConflictError',
    
    # Validation
    'InvalidArtistNameError',
    'InvalidChannelError',
    'InvalidArtistDataError',
    
    # Delete
    'ArtistHasSongsError',
    'ArtistDeleteError',
    'ArtistDeleteWithSongsError',
    
    # Bulk
    'BulkDeleteError',
    'BulkUpdateError',
    'BulkInsertError',
    'EmptySelectionError',
    'BulkValidationError',
    
    # Database
    'ArtistDatabaseError',
    'ArtistConnectionError',
    'ArtistTransactionError',
    
    # Filter
    'InvalidFilterError',
    'InvalidSortError',
    
    # Permission
    'ArtistPermissionError',
    
    # Helpers
    'create_artist_error_from_db_error',
    'create_bulk_error_from_results',
]