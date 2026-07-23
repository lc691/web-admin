"""
Channel Validator - Complete Implementation

Validator untuk semua business rules terkait Channel dengan:
- Field-level validation
- Cross-field validation
- Database uniqueness checks
- Bulk validation
- Detailed error messages
- Integration with exceptions
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

from app.music.repositories.channels.repository import ChannelRepository
from app.music.repositories.channels.bulk import ChannelBulkRepository
from app.music.services.channels.exceptions import (
    ChannelNotFoundError,
    DuplicateChannelNameError,
    DuplicateChannelEmailError,
    InvalidChannelNameError,
    InvalidChannelEmailError,
    InvalidChannelPasswordError,
    InvalidChannelNotesError,
    InvalidChannelVermukError,
    InvalidChannelDataError,
    InvalidFilterError,
    InvalidSortError,
    InvalidPaginationError,
    BulkValidationError,
    ChannelsNotFoundError,
)


class ChannelValidator:
    """
    Validator untuk semua business rules Channel.
    """
    
    # =====================================================
    # CONSTANTS
    # =====================================================
    
    NAME_MIN_LENGTH = 3
    NAME_MAX_LENGTH = 255
    EMAIL_MAX_LENGTH = 255
    NOTES_MAX_LENGTH = 10000
    PASSWORD_MIN_LENGTH = 6
    PASSWORD_MAX_LENGTH = 255
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    NAME_PATTERN = r'^[a-zA-Z0-9\s\-_.]+$'
    
    SORTABLE_COLUMNS = {'id', 'name', 'email', 'created_at', 'updated_at', 'vermuk'}
    ORDER_DIRECTIONS = {'asc', 'desc'}
    
    # =====================================================
    # FIELD VALIDATORS
    # =====================================================
    
    @staticmethod
    def validate_name(name: str) -> str:
        """
        Validate channel name.
        
        Args:
            name: Channel name to validate
            
        Returns:
            Trimmed and validated name
            
        Raises:
            InvalidChannelNameError: If name is invalid
        """
        if name is None:
            raise InvalidChannelNameError(
                name='',
                reason="Name is required"
            )
        
        name = name.strip()
        
        if not name:
            raise InvalidChannelNameError(
                name='',
                reason="Name cannot be empty or whitespace only"
            )
        
        if len(name) < ChannelValidator.NAME_MIN_LENGTH:
            raise InvalidChannelNameError(
                name=name,
                reason=f"Name must be at least {ChannelValidator.NAME_MIN_LENGTH} characters long"
            )
        
        if len(name) > ChannelValidator.NAME_MAX_LENGTH:
            raise InvalidChannelNameError(
                name=name,
                reason=f"Name cannot exceed {ChannelValidator.NAME_MAX_LENGTH} characters"
            )
        
        if not re.match(ChannelValidator.NAME_PATTERN, name):
            raise InvalidChannelNameError(
                name=name,
                reason="Name contains invalid characters. Allowed: letters, numbers, spaces, hyphens, underscores, dots"
            )
        
        return name
    
    @staticmethod
    def validate_email(email: Optional[str], required: bool = False) -> Optional[str]:
        """
        Validate channel email.
        
        Args:
            email: Email to validate
            required: Whether email is required
            
        Returns:
            Trimmed and validated email or None
            
        Raises:
            InvalidChannelEmailError: If email is invalid
        """
        if email is None:
            if required:
                raise InvalidChannelEmailError(
                    email='',
                    reason="Email is required"
                )
            return None
        
        email = email.strip().lower()
        
        if not email:
            if required:
                raise InvalidChannelEmailError(
                    email='',
                    reason="Email cannot be empty"
                )
            return None
        
        if len(email) > ChannelValidator.EMAIL_MAX_LENGTH:
            raise InvalidChannelEmailError(
                email=email,
                reason=f"Email cannot exceed {ChannelValidator.EMAIL_MAX_LENGTH} characters"
            )
        
        if not re.match(ChannelValidator.EMAIL_PATTERN, email):
            raise InvalidChannelEmailError(
                email=email,
                reason="Invalid email format"
            )
        
        return email
    
    @staticmethod
    def validate_password(password: Optional[str]) -> Optional[str]:
        """
        Validate channel password.
        
        Args:
            password: Password to validate
            
        Returns:
            Trimmed password or None
            
        Raises:
            InvalidChannelPasswordError: If password is invalid
        """
        if password is None:
            return None
        
        password = password.strip()
        
        if not password:
            return None
        
        if len(password) < ChannelValidator.PASSWORD_MIN_LENGTH:
            raise InvalidChannelPasswordError(
                reason=f"Password must be at least {ChannelValidator.PASSWORD_MIN_LENGTH} characters long"
            )
        
        if len(password) > ChannelValidator.PASSWORD_MAX_LENGTH:
            raise InvalidChannelPasswordError(
                reason=f"Password cannot exceed {ChannelValidator.PASSWORD_MAX_LENGTH} characters"
            )
        
        return password
    
    @staticmethod
    def validate_notes(notes: Optional[str]) -> Optional[str]:
        """
        Validate channel notes.
        
        Args:
            notes: Notes to validate
            
        Returns:
            Trimmed notes or None
            
        Raises:
            InvalidChannelNotesError: If notes are invalid
        """
        if notes is None:
            return None
        
        notes = notes.strip()
        
        if not notes:
            return None
        
        if len(notes) > ChannelValidator.NOTES_MAX_LENGTH:
            raise InvalidChannelNotesError(
                reason=f"Notes cannot exceed {ChannelValidator.NOTES_MAX_LENGTH} characters"
            )
        
        return notes
    
    @staticmethod
    def validate_vermuk(vermuk: Any) -> bool:
        """
        Validate vermuk status.
        
        Args:
            vermuk: Vermuk status
            
        Returns:
            Boolean value
            
        Raises:
            InvalidChannelVermukError: If vermuk is invalid
        """
        if isinstance(vermuk, bool):
            return vermuk
        
        if isinstance(vermuk, str):
            if vermuk.lower() in ('true', '1', 'yes', 'on'):
                return True
            if vermuk.lower() in ('false', '0', 'no', 'off'):
                return False
        
        if isinstance(vermuk, (int, float)):
            return bool(vermuk)
        
        raise InvalidChannelVermukError(
            vermuk=vermuk,
            reason="Must be a boolean value (True/False, 0/1, yes/no)"
        )
    
    # =====================================================
    # UNIQUENESS VALIDATORS
    # =====================================================
    
    @staticmethod
    def validate_unique_name(
        cursor,
        name: str,
        exclude_id: Optional[int] = None
    ) -> None:
        """
        Validate name uniqueness.
        
        Args:
            cursor: Database cursor
            name: Name to check
            exclude_id: ID to exclude (for updates)
            
        Raises:
            DuplicateChannelNameError: If name already exists
        """
        exists = ChannelRepository.exists_name(cursor, name, exclude_id=exclude_id)
        
        if exists:
            # Get existing channel info for better error message
            existing = None
            try:
                cursor.execute("""
                    SELECT id, name, email
                    FROM channels
                    WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                """, (name,))
                existing = cursor.fetchone()
            except:
                pass
            
            raise DuplicateChannelNameError(
                name=name,
                existing_id=existing['id'] if existing else None
            )
    
    @staticmethod
    def validate_unique_email(
        cursor,
        email: str,
        exclude_id: Optional[int] = None
    ) -> None:
        """
        Validate email uniqueness.
        
        Args:
            cursor: Database cursor
            email: Email to check
            exclude_id: ID to exclude (for updates)
            
        Raises:
            DuplicateChannelEmailError: If email already exists
        """
        if not email:
            return
        
        exists = ChannelRepository.exists_email(cursor, email, exclude_id=exclude_id)
        
        if exists:
            # Get existing channel info for better error message
            existing = None
            try:
                cursor.execute("""
                    SELECT id, name, email
                    FROM channels
                    WHERE email = %s
                """, (email,))
                existing = cursor.fetchone()
            except:
                pass
            
            raise DuplicateChannelEmailError(
                email=email,
                existing_id=existing['id'] if existing else None
            )
    
    # =====================================================
    # EXISTENCE VALIDATORS
    # =====================================================
    
    @staticmethod
    def validate_channel_exists(
        cursor,
        channel_id: int
    ) -> None:
        """
        Validate that a channel exists.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID to check
            
        Raises:
            ChannelNotFoundError: If channel doesn't exist
        """
        if not ChannelRepository.exists(cursor, channel_id):
            raise ChannelNotFoundError(channel_id=channel_id)
    
    @staticmethod
    def validate_channels_exist(
        cursor,
        channel_ids: List[int]
    ) -> List[int]:
        """
        Validate that multiple channels exist.
        
        Args:
            cursor: Database cursor
            channel_ids: List of channel IDs to check
            
        Returns:
            List of existing IDs
            
        Raises:
            ChannelsNotFoundError: If any channels don't exist
        """
        if not channel_ids:
            return []
        
        existing_ids = ChannelBulkRepository.bulk_exists(cursor, channel_ids)
        not_found = [id for id in channel_ids if id not in existing_ids]
        
        if not_found:
            raise ChannelsNotFoundError(
                channel_ids=channel_ids,
                not_found=not_found
            )
        
        return existing_ids
    
    # =====================================================
    # FILTER/SORT/PAGINATION VALIDATORS
    # =====================================================
    
    @staticmethod
    def validate_filter_params(filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate filter parameters.
        
        Args:
            filters: Filter parameters
            
        Returns:
            Validated and cleaned filters
            
        Raises:
            InvalidFilterError: If any filter is invalid
        """
        validated = {}
        
        # Keyword
        if filters.get('keyword'):
            keyword = str(filters['keyword']).strip()
            if keyword:
                validated['keyword'] = keyword
        
        # Vermuk
        if 'vermuk' in filters and filters['vermuk'] is not None:
            try:
                validated['vermuk'] = ChannelValidator.validate_vermuk(filters['vermuk'])
            except InvalidChannelVermukError as e:
                raise InvalidFilterError(
                    filter_param='vermuk',
                    filter_value=filters['vermuk'],
                    reason=str(e)
                )
        
        # Email
        if filters.get('email'):
            try:
                validated['email'] = ChannelValidator.validate_email(filters['email'])
            except InvalidChannelEmailError as e:
                raise InvalidFilterError(
                    filter_param='email',
                    filter_value=filters['email'],
                    reason=str(e)
                )
        
        # Date range
        if filters.get('date_from'):
            try:
                if isinstance(filters['date_from'], str):
                    validated['date_from'] = datetime.fromisoformat(filters['date_from'])
                else:
                    validated['date_from'] = filters['date_from']
            except ValueError as e:
                raise InvalidFilterError(
                    filter_param='date_from',
                    filter_value=filters['date_from'],
                    reason=f"Invalid date format: {e}"
                )
        
        if filters.get('date_to'):
            try:
                if isinstance(filters['date_to'], str):
                    validated['date_to'] = datetime.fromisoformat(filters['date_to'])
                else:
                    validated['date_to'] = filters['date_to']
            except ValueError as e:
                raise InvalidFilterError(
                    filter_param='date_to',
                    filter_value=filters['date_to'],
                    reason=f"Invalid date format: {e}"
                )
        
        # Numeric filters
        for param in ['min_artists', 'max_artists', 'min_songs', 'max_songs']:
            if param in filters and filters[param] is not None:
                try:
                    value = int(filters[param])
                    if value < 0:
                        raise ValueError(f"{param} cannot be negative")
                    validated[param] = value
                except (ValueError, TypeError) as e:
                    raise InvalidFilterError(
                        filter_param=param,
                        filter_value=filters[param],
                        reason=f"Must be a positive integer: {e}"
                    )
        
        # Boolean filters
        for param in ['has_artists', 'has_songs']:
            if param in filters and filters[param] is not None:
                try:
                    validated[param] = bool(filters[param])
                except:
                    raise InvalidFilterError(
                        filter_param=param,
                        filter_value=filters[param],
                        reason="Must be a boolean value"
                    )
        
        return validated
    
    @staticmethod
    def validate_sort_params(
        order_by: str,
        order_dir: str
    ) -> Tuple[str, str]:
        """
        Validate sort parameters.
        
        Args:
            order_by: Sort column
            order_dir: Sort direction
            
        Returns:
            Tuple of (validated_order_by, validated_order_dir)
            
        Raises:
            InvalidSortError: If sort parameters are invalid
        """
        # Validate order_by
        if not order_by:
            order_by = 'created_at'
        
        if order_by not in ChannelValidator.SORTABLE_COLUMNS:
            raise InvalidSortError(
                sort_column=order_by,
                reason=f"Invalid sort column. Allowed: {', '.join(ChannelValidator.SORTABLE_COLUMNS)}"
            )
        
        # Validate order_dir
        order_dir = str(order_dir).lower()
        if order_dir not in ChannelValidator.ORDER_DIRECTIONS:
            raise InvalidSortError(
                sort_column=order_by,
                sort_direction=order_dir,
                reason=f"Invalid sort direction. Allowed: {', '.join(ChannelValidator.ORDER_DIRECTIONS)}"
            )
        
        return order_by, order_dir
    
    @staticmethod
    def validate_pagination_params(
        start: int,
        length: int,
        max_length: int = 1000
    ) -> Tuple[int, int]:
        """
        Validate pagination parameters.
        
        Args:
            start: Start offset
            length: Number of items
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (validated_start, validated_length)
            
        Raises:
            InvalidPaginationError: If pagination parameters are invalid
        """
        try:
            start = int(start)
            if start < 0:
                raise ValueError("Cannot be negative")
        except (ValueError, TypeError) as e:
            raise InvalidPaginationError(
                param='start',
                value=start,
                reason=f"Invalid start value: {e}"
            )
        
        try:
            length = int(length)
            if length < 0:
                raise ValueError("Cannot be negative")
            if length > max_length:
                raise ValueError(f"Cannot exceed {max_length}")
        except (ValueError, TypeError) as e:
            raise InvalidPaginationError(
                param='length',
                value=length,
                reason=f"Invalid length value: {e}"
            )
        
        return start, length
    
    # =====================================================
    # COMPLETE VALIDATION METHODS
    # =====================================================
    
    @classmethod
    def validate_create(
        cls,
        cursor,
        *,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate all data for creating a channel.
        
        Args:
            cursor: Database cursor
            name: Channel name
            email: Channel email
            password: Channel password
            vermuk: Vermuk status
            notes: Channel notes
            
        Returns:
            Dict with validated and cleaned data
            
        Raises:
            Various exceptions if validation fails
        """
        errors = {}
        validated_data = {}
        
        try:
            validated_data['name'] = cls.validate_name(name)
        except InvalidChannelNameError as e:
            errors['name'] = str(e)
        
        try:
            validated_data['email'] = cls.validate_email(email)
        except InvalidChannelEmailError as e:
            errors['email'] = str(e)
        
        try:
            validated_data['password'] = cls.validate_password(password)
        except InvalidChannelPasswordError as e:
            errors['password'] = str(e)
        
        try:
            validated_data['vermuk'] = cls.validate_vermuk(vermuk)
        except InvalidChannelVermukError as e:
            errors['vermuk'] = str(e)
        
        try:
            validated_data['notes'] = cls.validate_notes(notes)
        except InvalidChannelNotesError as e:
            errors['notes'] = str(e)
        
        # Check for validation errors before database checks
        if errors:
            raise InvalidChannelDataError(
                message="Channel data validation failed",
                errors=errors
            )
        
        # Database uniqueness checks
        try:
            if 'name' in validated_data:
                cls.validate_unique_name(cursor, validated_data['name'])
        except DuplicateChannelNameError as e:
            errors['name'] = str(e)
        
        try:
            if validated_data.get('email'):
                cls.validate_unique_email(cursor, validated_data['email'])
        except DuplicateChannelEmailError as e:
            errors['email'] = str(e)
        
        if errors:
            raise InvalidChannelDataError(
                message="Channel data validation failed",
                errors=errors
            )
        
        return validated_data
    
    @classmethod
    def validate_update(
        cls,
        cursor,
        *,
        channel_id: int,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate all data for updating a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            name: Channel name
            email: Channel email
            password: Channel password
            vermuk: Vermuk status
            notes: Channel notes
            
        Returns:
            Dict with validated and cleaned data
            
        Raises:
            Various exceptions if validation fails
        """
        errors = {}
        validated_data = {'id': channel_id}
        
        # Check channel exists first
        try:
            cls.validate_channel_exists(cursor, channel_id)
        except ChannelNotFoundError as e:
            errors['channel_id'] = str(e)
            raise
        
        try:
            validated_data['name'] = cls.validate_name(name)
        except InvalidChannelNameError as e:
            errors['name'] = str(e)
        
        try:
            validated_data['email'] = cls.validate_email(email)
        except InvalidChannelEmailError as e:
            errors['email'] = str(e)
        
        try:
            validated_data['password'] = cls.validate_password(password)
        except InvalidChannelPasswordError as e:
            errors['password'] = str(e)
        
        try:
            validated_data['vermuk'] = cls.validate_vermuk(vermuk)
        except InvalidChannelVermukError as e:
            errors['vermuk'] = str(e)
        
        try:
            validated_data['notes'] = cls.validate_notes(notes)
        except InvalidChannelNotesError as e:
            errors['notes'] = str(e)
        
        # Check for validation errors before database checks
        if errors:
            raise InvalidChannelDataError(
                message="Channel data validation failed",
                errors=errors
            )
        
        # Database uniqueness checks (excluding current channel)
        try:
            if 'name' in validated_data:
                cls.validate_unique_name(cursor, validated_data['name'], exclude_id=channel_id)
        except DuplicateChannelNameError as e:
            errors['name'] = str(e)
        
        try:
            if validated_data.get('email'):
                cls.validate_unique_email(cursor, validated_data['email'], exclude_id=channel_id)
        except DuplicateChannelEmailError as e:
            errors['email'] = str(e)
        
        if errors:
            raise InvalidChannelDataError(
                message="Channel data validation failed",
                errors=errors
            )
        
        return validated_data
    
    @classmethod
    def validate_bulk_delete(
        cls,
        cursor,
        channel_ids: List[int],
        allow_empty: bool = False
    ) -> Dict[str, Any]:
        """
        Validate bulk delete operation.
        
        Args:
            cursor: Database cursor
            channel_ids: List of channel IDs
            allow_empty: Allow empty list
            
        Returns:
            Dict with validated data
            
        Raises:
            BulkValidationError: If validation fails
        """
        if not channel_ids:
            if allow_empty:
                return {'channel_ids': [], 'valid_count': 0}
            raise BulkValidationError(
                message="No channel IDs provided for bulk delete",
                validation_errors={'channel_ids': ['List cannot be empty']}
            )
        
        # Check for duplicates
        unique_ids = list(set(channel_ids))
        if len(unique_ids) != len(channel_ids):
            duplicates = [id for id in unique_ids if channel_ids.count(id) > 1]
            raise BulkValidationError(
                message="Duplicate channel IDs found",
                validation_errors={'channel_ids': [f'Duplicate IDs: {duplicates}']}
            )
        
        # Check existence
        try:
            existing_ids = cls.validate_channels_exist(cursor, unique_ids)
        except ChannelsNotFoundError as e:
            raise BulkValidationError(
                message="Some channels not found",
                validation_errors={'channel_ids': [str(e)]}
            )
        
        return {
            'channel_ids': existing_ids,
            'valid_count': len(existing_ids)
        }
    
    @classmethod
    def validate_bulk_update(
        cls,
        cursor,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate bulk update operation.
        
        Args:
            cursor: Database cursor
            updates: List of update data
            
        Returns:
            Dict with validated data
            
        Raises:
            BulkValidationError: If validation fails
        """
        if not updates:
            raise BulkValidationError(
                message="No updates provided",
                validation_errors={'updates': ['List cannot be empty']}
            )
        
        validation_errors = {}
        validated_updates = []
        channel_ids = []
        
        for idx, update in enumerate(updates):
            update_errors = {}
            
            # Validate ID
            channel_id = update.get('id')
            if not channel_id:
                update_errors['id'] = 'Missing or invalid ID'
            elif not isinstance(channel_id, int):
                update_errors['id'] = 'ID must be an integer'
            else:
                channel_ids.append(channel_id)
            
            # Validate fields
            if update.get('name') is not None:
                try:
                    cls.validate_name(update['name'])
                except InvalidChannelNameError as e:
                    update_errors['name'] = str(e)
            
            if update.get('email') is not None:
                try:
                    cls.validate_email(update['email'])
                except InvalidChannelEmailError as e:
                    update_errors['email'] = str(e)
            
            if update.get('password') is not None:
                try:
                    cls.validate_password(update['password'])
                except InvalidChannelPasswordError as e:
                    update_errors['password'] = str(e)
            
            if update.get('vermuk') is not None:
                try:
                    cls.validate_vermuk(update['vermuk'])
                except InvalidChannelVermukError as e:
                    update_errors['vermuk'] = str(e)
            
            if update.get('notes') is not None:
                try:
                    cls.validate_notes(update['notes'])
                except InvalidChannelNotesError as e:
                    update_errors['notes'] = str(e)
            
            if update_errors:
                validation_errors[idx] = update_errors
            else:
                validated_updates.append(update)
        
        # Check channel existence
        if channel_ids:
            try:
                cls.validate_channels_exist(cursor, channel_ids)
            except ChannelsNotFoundError as e:
                validation_errors['channels'] = [str(e)]
        
        if validation_errors:
            raise BulkValidationError(
                message="Bulk update validation failed",
                validation_errors=validation_errors
            )
        
        return {
            'validated_updates': validated_updates,
            'valid_count': len(validated_updates)
        }
    
    # =====================================================
    # HELPER METHODS
    # =====================================================
    
    @staticmethod
    def get_validation_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary of validation results.
        
        Args:
            data: Data to summarize
            
        Returns:
            Dict with validation summary
        """
        summary = {
            'valid': True,
            'errors': 0,
            'warnings': 0,
            'fields': {}
        }
        
        for key, value in data.items():
            if isinstance(value, dict) and 'errors' in value:
                summary['valid'] = False
                summary['errors'] += len(value['errors'])
                summary['fields'][key] = {
                    'valid': False,
                    'error_count': len(value['errors'])
                }
            else:
                summary['fields'][key] = {
                    'valid': True,
                    'error_count': 0
                }
        
        return summary