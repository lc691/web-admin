"""
Channels Services Package

Package untuk semua service layer Channel dengan:
- Business logic operations
- Data validation
- DTO mapping
- Exception handling
- Service orchestration

Export semua public classes untuk kemudahan import.
"""

from .service import ChannelService
from .validator import ChannelValidator
from .mapper import (
    ChannelMapper,
    ChannelDTO,
    ChannelCreateDTO,
    ChannelUpdateDTO,
    ChannelFilterDTO,
    ChannelStatsDTO,
    ChannelActivityDTO,
    ChannelListDTO,
)
from .exceptions import (
    ChannelError,
    ChannelNotFoundError,
    ChannelsNotFoundError,
    DuplicateChannelNameError,
    DuplicateChannelEmailError,
    InvalidChannelNameError,
    InvalidChannelEmailError,
    InvalidChannelPasswordError,
    InvalidChannelNotesError,
    InvalidChannelVermukError,
    InvalidChannelDataError,
    BulkChannelError,
    BulkDeleteError,
    BulkUpdateError,
    BulkInsertError,
    BulkValidationError,
    ChannelPermissionError,
    ChannelTransactionError,
    ChannelConnectionError,
    InvalidFilterError,
    InvalidSortError,
    InvalidPaginationError,
    create_channel_error_from_db_error,
    create_bulk_error_from_results,
)

__all__ = [
    # Service
    'ChannelService',
    
    # Validator
    'ChannelValidator',
    
    # Mapper & DTOs
    'ChannelMapper',
    'ChannelDTO',
    'ChannelCreateDTO',
    'ChannelUpdateDTO',
    'ChannelFilterDTO',
    'ChannelStatsDTO',
    'ChannelActivityDTO',
    'ChannelListDTO',
    
    # Exceptions
    'ChannelError',
    'ChannelNotFoundError',
    'ChannelsNotFoundError',
    'DuplicateChannelNameError',
    'DuplicateChannelEmailError',
    'InvalidChannelNameError',
    'InvalidChannelEmailError',
    'InvalidChannelPasswordError',
    'InvalidChannelNotesError',
    'InvalidChannelVermukError',
    'InvalidChannelDataError',
    'BulkChannelError',
    'BulkDeleteError',
    'BulkUpdateError',
    'BulkInsertError',
    'BulkValidationError',
    'ChannelPermissionError',
    'ChannelTransactionError',
    'ChannelConnectionError',
    'InvalidFilterError',
    'InvalidSortError',
    'InvalidPaginationError',
    'create_channel_error_from_db_error',
    'create_bulk_error_from_results',
]

# Version info
__version__ = '1.0.0'
__author__ = 'Music Team'

# Package metadata
PACKAGE_METADATA = {
    'name': 'Channel Services',
    'version': __version__,
    'description': 'Business logic layer for Channel management',
    'author': __author__,
}