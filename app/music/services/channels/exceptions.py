"""
Channel Exceptions - Complete Implementation

Exception hierarchy untuk semua error yang terkait dengan Channel operations.
Menggunakan inheritance untuk memudahkan error handling dan logging.
"""

from typing import Any, Dict, List, Optional


# =====================================================
# BASE EXCEPTION
# =====================================================

class ChannelError(Exception):
    """
    Base exception untuk seluruh Channel module.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None
    ):
        self.message = message
        self.details = details or {}
        self.code = code or 'CHANNEL_ERROR'
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

class ChannelNotFoundError(ChannelError):
    """
    Channel tidak ditemukan.
    """
    
    def __init__(
        self,
        channel_id: Optional[int] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if channel_id:
            message = f"Channel with ID '{channel_id}' not found"
            code = 'CHANNEL_NOT_FOUND_BY_ID'
        elif name:
            message = f"Channel with name '{name}' not found"
            code = 'CHANNEL_NOT_FOUND_BY_NAME'
        elif email:
            message = f"Channel with email '{email}' not found"
            code = 'CHANNEL_NOT_FOUND_BY_EMAIL'
        else:
            message = "Channel not found"
            code = 'CHANNEL_NOT_FOUND'
        
        details = details or {}
        if channel_id:
            details['channel_id'] = channel_id
        if name:
            details['name'] = name
        if email:
            details['email'] = email
        
        super().__init__(message, details, code)


class ChannelsNotFoundError(ChannelError):
    """
    Multiple channels tidak ditemukan.
    """
    
    def __init__(
        self,
        channel_ids: List[int],
        not_found: List[int],
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Channels not found: {len(not_found)} of {len(channel_ids)} IDs missing"
        code = 'CHANNELS_NOT_FOUND'
        
        details = details or {}
        details['requested_ids'] = channel_ids
        details['not_found_ids'] = not_found
        details['found_count'] = len(channel_ids) - len(not_found)
        
        super().__init__(message, details, code)


# =====================================================
# VALIDATION ERRORS
# =====================================================

class InvalidChannelNameError(ChannelError):
    """
    Nama channel tidak valid.
    """
    
    def __init__(
        self,
        name: str,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Invalid channel name '{name}': {reason}"
        else:
            message = f"Invalid channel name '{name}'"
        
        code = 'INVALID_CHANNEL_NAME'
        
        details = details or {}
        details['name'] = name
        
        super().__init__(message, details, code)


class InvalidChannelEmailError(ChannelError):
    """
    Email channel tidak valid.
    """
    
    def __init__(
        self,
        email: str,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Invalid channel email '{email}': {reason}"
        else:
            message = f"Invalid channel email '{email}'"
        
        code = 'INVALID_CHANNEL_EMAIL'
        
        details = details or {}
        details['email'] = email
        
        super().__init__(message, details, code)


class InvalidChannelPasswordError(ChannelError):
    """
    Password channel tidak valid.
    """
    
    def __init__(
        self,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Invalid channel password: {reason}"
        else:
            message = "Invalid channel password"
        
        code = 'INVALID_CHANNEL_PASSWORD'
        
        super().__init__(message, details, code)


class InvalidChannelVermukError(ChannelError):
    """
    Vermuk status tidak valid.
    """
    
    def __init__(
        self,
        vermuk: Any,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Invalid vermuk status '{vermuk}': {reason}"
        else:
            message = f"Invalid vermuk status '{vermuk}'"
        
        code = 'INVALID_CHANNEL_VERMUK'
        
        details = details or {}
        details['vermuk'] = vermuk
        
        super().__init__(message, details, code)


class InvalidChannelNotesError(ChannelError):
    """
    Notes channel tidak valid.
    """
    
    def __init__(
        self,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Invalid channel notes: {reason}"
        code = 'INVALID_CHANNEL_NOTES'
        
        super().__init__(message, details, code)


class InvalidChannelDataError(ChannelError):
    """
    Data channel tidak valid secara umum.
    """
    
    def __init__(
        self,
        message: str,
        errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        code = 'INVALID_CHANNEL_DATA'
        
        details = details or {}
        if errors:
            details['errors'] = errors
        
        super().__init__(message, details, code)


# =====================================================
# DUPLICATE ERRORS
# =====================================================

class DuplicateChannelNameError(ChannelError):
    """
    Nama channel sudah digunakan.
    """
    
    def __init__(
        self,
        name: str,
        existing_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Channel with name '{name}' already exists"
        code = 'DUPLICATE_CHANNEL_NAME'
        
        details = details or {}
        details['name'] = name
        if existing_id:
            details['existing_id'] = existing_id
        
        super().__init__(message, details, code)


class DuplicateChannelEmailError(ChannelError):
    """
    Email channel sudah digunakan.
    """
    
    def __init__(
        self,
        email: str,
        existing_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Channel with email '{email}' already exists"
        code = 'DUPLICATE_CHANNEL_EMAIL'
        
        details = details or {}
        details['email'] = email
        if existing_id:
            details['existing_id'] = existing_id
        
        super().__init__(message, details, code)


class DuplicateChannelOperationError(ChannelError):
    """
    Duplicate operation error (bulk operations).
    """
    
    def __init__(
        self,
        duplicate_ids: List[int],
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if message is None:
            message = f"Duplicate channel IDs detected: {duplicate_ids}"
        
        code = 'DUPLICATE_CHANNEL_OPERATION'
        
        details = details or {}
        details['duplicate_ids'] = duplicate_ids
        
        super().__init__(message, details, code)


# =====================================================
# PERMISSION ERRORS
# =====================================================

class ChannelPermissionError(ChannelError):
    """
    User tidak memiliki permission untuk operasi channel.
    """
    
    def __init__(
        self,
        action: str,
        channel_id: Optional[int] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Permission denied to {action} channel"
        
        if channel_id:
            message += f" (ID: {channel_id})"
        
        code = 'CHANNEL_PERMISSION_DENIED'
        
        details = details or {}
        details['action'] = action
        if channel_id:
            details['channel_id'] = channel_id
        if user_id:
            details['user_id'] = user_id
        
        super().__init__(message, details, code)


# =====================================================
# BULK OPERATIONS ERRORS
# =====================================================

class BulkChannelError(ChannelError):
    """
    Error operasi bulk secara umum.
    """
    
    def __init__(
        self,
        message: str,
        failed_ids: Optional[List[int]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        code = 'BULK_CHANNEL_ERROR'
        
        details = details or {}
        if failed_ids:
            details['failed_ids'] = failed_ids
            details['failed_count'] = len(failed_ids)
        if errors:
            details['errors'] = errors
            details['error_count'] = len(errors)
        
        super().__init__(message, details, code)


class BulkDeleteError(BulkChannelError):
    """
    Error bulk delete.
    """
    
    def __init__(
        self,
        message: str = "Bulk delete failed",
        failed_ids: Optional[List[int]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details['operation'] = 'delete'
        super().__init__(message, failed_ids, errors, details)


class BulkUpdateError(BulkChannelError):
    """
    Error bulk update.
    """
    
    def __init__(
        self,
        message: str = "Bulk update failed",
        failed_ids: Optional[List[int]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details['operation'] = 'update'
        super().__init__(message, failed_ids, errors, details)


class BulkInsertError(BulkChannelError):
    """
    Error bulk insert.
    """
    
    def __init__(
        self,
        message: str = "Bulk insert failed",
        failed_items: Optional[List[Dict[str, Any]]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details['operation'] = 'insert'
        if failed_items:
            details['failed_items'] = failed_items
            details['failed_count'] = len(failed_items)
        super().__init__(message, None, errors, details)


class BulkValidationError(BulkChannelError):
    """
    Error validasi bulk.
    """
    
    def __init__(
        self,
        message: str,
        validation_errors: Dict[int, List[str]],
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details['validation_errors'] = validation_errors
        details['error_count'] = len(validation_errors)
        super().__init__(message, None, None, details)


# =====================================================
# TRANSACTION ERRORS
# =====================================================

class ChannelTransactionError(ChannelError):
    """
    Error database transaction.
    """
    
    def __init__(
        self,
        message: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ):
        code = 'CHANNEL_TRANSACTION_ERROR'
        
        details = details or {}
        details['operation'] = operation
        
        super().__init__(message, details, code)


class ChannelConnectionError(ChannelError):
    """
    Error database connection.
    """
    
    def __init__(
        self,
        message: str = "Database connection error",
        details: Optional[Dict[str, Any]] = None
    ):
        code = 'CHANNEL_CONNECTION_ERROR'
        super().__init__(message, details, code)


# =====================================================
# FILTER / QUERY ERRORS
# =====================================================

class InvalidFilterError(ChannelError):
    """
    Invalid filter parameters.
    """
    
    def __init__(
        self,
        filter_param: str,
        filter_value: Any,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Invalid filter '{filter_param}': {reason}"
        code = 'INVALID_FILTER'
        
        details = details or {}
        details['filter_param'] = filter_param
        details['filter_value'] = filter_value
        details['reason'] = reason
        
        super().__init__(message, details, code)


class InvalidSortError(ChannelError):
    """
    Invalid sort parameters.
    """
    
    def __init__(
        self,
        sort_column: str,
        sort_direction: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if sort_direction:
            message = f"Invalid sort: column '{sort_column}' or direction '{sort_direction}'"
        else:
            message = f"Invalid sort column '{sort_column}'"
        
        code = 'INVALID_SORT'
        
        details = details or {}
        details['sort_column'] = sort_column
        if sort_direction:
            details['sort_direction'] = sort_direction
        
        super().__init__(message, details, code)


class InvalidPaginationError(ChannelError):
    """
    Invalid pagination parameters.
    """
    
    def __init__(
        self,
        param: str,
        value: Any,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Invalid pagination parameter '{param}': {reason}"
        code = 'INVALID_PAGINATION'
        
        details = details or {}
        details['param'] = param
        details['value'] = value
        details['reason'] = reason
        
        super().__init__(message, details, code)


# =====================================================
# FACTORY / HELPER FUNCTIONS
# =====================================================

def create_channel_error_from_db_error(error: Exception) -> ChannelError:
    """
    Create appropriate channel exception from database error.
    
    Args:
        error: Database error
        
    Returns:
        ChannelError instance
    """
    error_message = str(error).lower()
    
    if 'duplicate key' in error_message:
        if 'name' in error_message:
            return DuplicateChannelNameError('unknown_name')
        elif 'email' in error_message:
            return DuplicateChannelEmailError('unknown_email')
        else:
            return ChannelError(f"Duplicate record: {str(error)}", code='DB_DUPLICATE')
    
    if 'not found' in error_message or 'does not exist' in error_message:
        return ChannelNotFoundError()
    
    if 'connection' in error_message:
        return ChannelConnectionError(str(error))
    
    return ChannelError(f"Database error: {str(error)}", code='DB_ERROR')


def create_bulk_error_from_results(
    action: str,
    total: int,
    success_count: int,
    failed_count: int
) -> Optional[BulkChannelError]:
    """
    Create bulk error if there were failures.
    
    Args:
        action: Action name (delete, update, insert)
        total: Total items processed
        success_count: Successful items
        failed_count: Failed items
        
    Returns:
        BulkChannelError if there were failures, None otherwise
    """
    if failed_count == 0:
        return None
    
    if action == 'delete':
        return BulkDeleteError(
            message=f"Bulk delete partially failed: {failed_count} of {total} failed",
            details={
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )
    elif action == 'update':
        return BulkUpdateError(
            message=f"Bulk update partially failed: {failed_count} of {total} failed",
            details={
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )
    elif action == 'insert':
        return BulkInsertError(
            message=f"Bulk insert partially failed: {failed_count} of {total} failed",
            details={
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )
    else:
        return BulkChannelError(
            message=f"Bulk operation partially failed: {failed_count} of {total} failed",
            details={
                'action': action,
                'total': total,
                'success_count': success_count,
                'failed_count': failed_count,
            }
        )