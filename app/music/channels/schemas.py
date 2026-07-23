"""
Channel Schemas - Complete Implementation

Pydantic schemas untuk Channel dengan:
- Request/Response validation
- Nested schemas untuk statistics
- Bulk operation schemas
- Filter schemas
- Detailed field validations
- Type hints and documentation
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from pydantic.types import PastDate, FutureDate


# =====================================================
# ENUMS
# =====================================================

class ChannelSortField(str, Enum):
    """Sort fields untuk Channel."""
    ID = "id"
    NAME = "name"
    EMAIL = "email"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    VERMUK = "vermuk"
    ARTISTS = "artists"
    SONGS = "songs"


class SortDirection(str, Enum):
    """Sort direction."""
    ASC = "asc"
    DESC = "desc"


class ChannelLevel(str, Enum):
    """Channel activity level."""
    HIGHLY_ACTIVE = "Highly Active"
    ACTIVE = "Active"
    MODERATELY_ACTIVE = "Moderately Active"
    LOW_ACTIVITY = "Low Activity"
    INACTIVE = "Inactive"


# =====================================================
# BASE SCHEMA
# =====================================================

class ChannelBase(BaseModel):
    """
    Field dasar Channel.
    """
    name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Channel name (unique, case-insensitive)"
    )
    email: Optional[EmailStr] = Field(
        None,
        max_length=255,
        description="Channel email (unique if provided)"
    )
    password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=255,
        description="Channel password (optional)"
    )
    vermuk: bool = Field(
        False,
        description="Vermuk status flag"
    )
    notes: Optional[str] = Field(
        None,
        max_length=10000,
        description="Additional notes"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "My Music Channel",
                "email": "music@example.com",
                "password": "secure_password_123",
                "vermuk": False,
                "notes": "Main music distribution channel"
            }
        }
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate channel name."""
        v = v.strip()
        if not v:
            raise ValueError('Name cannot be empty')
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters')
        if len(v) > 255:
            raise ValueError('Name must be less than 255 characters')
        # Allow letters, numbers, spaces, hyphens, underscores, dots
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', v):
            raise ValueError(
                'Name contains invalid characters. '
                'Allowed: letters, numbers, spaces, hyphens, underscores, dots'
            )
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email (already validated by EmailStr)."""
        if v is not None:
            v = v.strip().lower()
            if len(v) > 255:
                raise ValueError('Email must be less than 255 characters')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password."""
        if v is not None:
            v = v.strip()
            if v and len(v) < 6:
                raise ValueError('Password must be at least 6 characters')
            if v and len(v) > 255:
                raise ValueError('Password must be less than 255 characters')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate notes."""
        if v is not None:
            v = v.strip()
            if v and len(v) > 10000:
                raise ValueError('Notes must be less than 10000 characters')
        return v


# =====================================================
# CREATE / UPDATE SCHEMAS
# =====================================================

class ChannelCreate(ChannelBase):
    """Schema untuk membuat channel."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Music Channel",
                "email": "new@example.com",
                "password": "secure_password_123",
                "vermuk": False,
                "notes": "New channel created via API"
            }
        }
    )


class ChannelUpdate(BaseModel):
    """
    Schema untuk mengubah channel.
    Semua field optional untuk partial update.
    """
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Channel name (unique, case-insensitive)"
    )
    email: Optional[EmailStr] = Field(
        None,
        max_length=255,
        description="Channel email (unique if provided)"
    )
    password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=255,
        description="Channel password (optional)"
    )
    vermuk: Optional[bool] = Field(
        None,
        description="Vermuk status flag"
    )
    notes: Optional[str] = Field(
        None,
        max_length=10000,
        description="Additional notes"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "Updated Channel Name",
                "email": "updated@example.com",
                "vermuk": True,
                "notes": "Updated notes"
            }
        }
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate channel name."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Name cannot be empty')
            if len(v) < 3:
                raise ValueError('Name must be at least 3 characters')
            if len(v) > 255:
                raise ValueError('Name must be less than 255 characters')
            import re
            if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', v):
                raise ValueError(
                    'Name contains invalid characters. '
                    'Allowed: letters, numbers, spaces, hyphens, underscores, dots'
                )
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email."""
        if v is not None:
            v = v.strip().lower()
            if len(v) > 255:
                raise ValueError('Email must be less than 255 characters')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password."""
        if v is not None:
            v = v.strip()
            if v and len(v) < 6:
                raise ValueError('Password must be at least 6 characters')
            if v and len(v) > 255:
                raise ValueError('Password must be less than 255 characters')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate notes."""
        if v is not None:
            v = v.strip()
            if v and len(v) > 10000:
                raise ValueError('Notes must be less than 10000 characters')
        return v


# =====================================================
# NOTES UPDATE SCHEMA
# =====================================================

class ChannelNotesUpdate(BaseModel):
    """
    Schema untuk update notes saja.
    Digunakan untuk PATCH /{channel_id}/notes endpoint.
    """
    notes: Optional[str] = Field(
        None,
        max_length=10000,
        description="New notes for the channel"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "notes": "Updated notes for the channel with new information"
            }
        }
    )

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate notes."""
        if v is not None:
            v = v.strip()
            if v and len(v) > 10000:
                raise ValueError('Notes must be less than 10000 characters')
        return v


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class ChannelStatusBreakdown(BaseModel):
    """Status breakdown untuk channel."""
    status: str = Field(..., description="Status name")
    count: int = Field(..., ge=0, description="Number of songs with this status")
    percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Percentage of total"
    )


class ChannelStats(BaseModel):
    """Statistics untuk channel."""
    total_artists: int = Field(0, ge=0, description="Total artists in channel")
    total_songs: int = Field(0, ge=0, description="Total songs in channel")
    uploaded_songs: int = Field(0, ge=0, description="Uploaded songs count")
    pending_songs: int = Field(0, ge=0, description="Pending songs count")
    takedown_songs: int = Field(0, ge=0, description="Takedown songs count")
    artists_with_songs: int = Field(0, ge=0, description="Artists with at least one song")
    uploaded_rate: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Upload rate percentage"
    )
    pending_rate: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Pending rate percentage"
    )
    days_active: int = Field(0, ge=0, description="Days since first song")
    songs_per_day: float = Field(0.0, ge=0, description="Average songs per day")
    earliest_release: Optional[datetime] = Field(
        None,
        description="Earliest song release date"
    )
    latest_release: Optional[datetime] = Field(
        None,
        description="Latest song release date"
    )
    status_breakdown: Optional[List[ChannelStatusBreakdown]] = Field(
        None,
        description="Breakdown by song status"
    )


class ChannelActivity(BaseModel):
    """Activity scoring untuk channel."""
    channel_id: int = Field(..., description="Channel ID")
    channel_name: str = Field(..., description="Channel name")
    total_songs: int = Field(0, ge=0, description="Total songs")
    total_artists: int = Field(0, ge=0, description="Total artists")
    recent_songs: int = Field(0, ge=0, description="Songs in last 30 days")
    recency_score: float = Field(0.0, ge=0, le=100, description="Recency score")
    consistency_score: float = Field(0.0, ge=0, le=100, description="Consistency score")
    engagement_score: float = Field(0.0, ge=0, le=100, description="Engagement score")
    growth_score: float = Field(0.0, ge=0, le=100, description="Growth score")
    overall_score: float = Field(0.0, ge=0, le=100, description="Overall activity score")
    level: ChannelLevel = Field(..., description="Activity level")
    last_activity: Optional[datetime] = Field(None, description="Last activity date")
    avg_songs_per_month: float = Field(0.0, ge=0, description="Average songs per month")
    upload_rate: float = Field(0.0, ge=0, le=100, description="Upload rate")


class ChannelResponse(BaseModel):
    """
    Response schema untuk Channel.
    """
    id: int = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    email: Optional[str] = Field(None, description="Channel email")
    vermuk: bool = Field(..., description="Vermuk status")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    total_artists: Optional[int] = Field(0, ge=0, description="Total artists")
    total_songs: Optional[int] = Field(0, ge=0, description="Total songs")
    uploaded_songs: Optional[int] = Field(0, ge=0, description="Uploaded songs")
    pending_songs: Optional[int] = Field(0, ge=0, description="Pending songs")
    takedown_songs: Optional[int] = Field(0, ge=0, description="Takedown songs")
    stats: Optional[ChannelStats] = Field(None, description="Channel statistics")
    activity: Optional[ChannelActivity] = Field(None, description="Activity scoring")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "My Music Channel",
                "email": "music@example.com",
                "vermuk": False,
                "notes": "Main music distribution channel",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "total_artists": 10,
                "total_songs": 50,
                "uploaded_songs": 40,
                "pending_songs": 8,
                "takedown_songs": 2,
                "stats": {
                    "total_artists": 10,
                    "total_songs": 50,
                    "uploaded_songs": 40,
                    "pending_songs": 8,
                    "takedown_songs": 2,
                    "uploaded_rate": 80.0,
                    "pending_rate": 16.0,
                    "days_active": 365
                }
            }
        }
    )


class ChannelListResponse(BaseModel):
    """
    Response schema untuk list channel dengan pagination.
    """
    data: List[ChannelResponse] = Field(..., description="List of channels")
    meta: Dict[str, Any] = Field(
        ...,
        description="Pagination and filter metadata"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "name": "Channel A",
                        "email": "a@example.com",
                        "vermuk": False,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "meta": {
                    "total": 100,
                    "page": 1,
                    "total_pages": 5,
                    "start": 0,
                    "length": 20,
                    "filters": {"keyword": "music"}
                }
            }
        }
    )


# =====================================================
# FILTER SCHEMAS
# =====================================================

class ChannelFilter(BaseModel):
    """
    Schema filter untuk DataTables dan list channel.
    """
    draw: int = Field(1, ge=1, description="DataTable draw counter")
    start: int = Field(0, ge=0, description="Pagination start offset")
    length: int = Field(25, ge=1, le=1000, description="Pagination length")
    
    search: Optional[str] = Field(
        None,
        max_length=255,
        description="Search keyword"
    )
    order_column: ChannelSortField = Field(
        ChannelSortField.CREATED_AT,
        description="Sort column"
    )
    order_dir: SortDirection = Field(
        SortDirection.DESC,
        description="Sort direction"
    )
    
    vermuk: Optional[bool] = Field(
        None,
        description="Filter by vermuk status"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Filter by exact email"
    )
    date_from: Optional[datetime] = Field(
        None,
        description="Filter by creation date (from)"
    )
    date_to: Optional[datetime] = Field(
        None,
        description="Filter by creation date (to)"
    )
    has_artists: Optional[bool] = Field(
        None,
        description="Filter channels with/without artists"
    )
    has_songs: Optional[bool] = Field(
        None,
        description="Filter channels with/without songs"
    )
    min_artists: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum number of artists"
    )
    max_artists: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum number of artists"
    )
    min_songs: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum number of songs"
    )
    max_songs: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum number of songs"
    )

    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        """Validate search term."""
        if v is not None:
            v = v.strip()
            if v and len(v) > 255:
                raise ValueError('Search term must be less than 255 characters')
        return v


class ChannelFilterRequest(BaseModel):
    """
    Alternative filter schema for API requests.
    """
    keyword: Optional[str] = Field(
        None,
        max_length=255,
        description="Search keyword (name, email, notes)"
    )
    vermuk: Optional[bool] = Field(None, description="Filter by vermuk status")
    email: Optional[EmailStr] = Field(None, description="Filter by exact email")
    date_from: Optional[datetime] = Field(None, description="Creation date from")
    date_to: Optional[datetime] = Field(None, description="Creation date to")
    has_artists: Optional[bool] = Field(None, description="Has artists")
    has_songs: Optional[bool] = Field(None, description="Has songs")
    min_artists: Optional[int] = Field(None, ge=0, description="Minimum artists")
    max_artists: Optional[int] = Field(None, ge=0, description="Maximum artists")
    min_songs: Optional[int] = Field(None, ge=0, description="Minimum songs")
    max_songs: Optional[int] = Field(None, ge=0, description="Maximum songs")
    order_by: ChannelSortField = Field(
        ChannelSortField.CREATED_AT,
        description="Sort by field"
    )
    order_dir: SortDirection = Field(
        SortDirection.DESC,
        description="Sort direction"
    )
    start: int = Field(0, ge=0, description="Pagination offset")
    length: int = Field(20, ge=1, le=1000, description="Pagination limit")


# =====================================================
# BULK OPERATION SCHEMAS
# =====================================================

class ChannelBulkDelete(BaseModel):
    """Schema untuk bulk delete channel."""
    ids: List[int] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of channel IDs to delete"
    )
    validate_existence: bool = Field(
        True,
        description="Validate all IDs exist before deletion"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [1, 2, 3, 4, 5],
                "validate_existence": True
            }
        }
    )

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v: List[int]) -> List[int]:
        """Validate channel IDs."""
        if not v:
            raise ValueError('IDs list cannot be empty')
        if len(v) > 1000:
            raise ValueError('Maximum 1000 IDs allowed')
        # Remove duplicates
        unique_ids = list(set(v))
        if len(unique_ids) != len(v):
            raise ValueError('Duplicate IDs detected')
        if any(id < 1 for id in v):
            raise ValueError('Invalid channel ID (must be positive integer)')
        return unique_ids


class ChannelBulkVermuk(BaseModel):
    """Schema untuk bulk update vermuk channel."""
    ids: List[int] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of channel IDs to update"
    )
    vermuk: bool = Field(
        ...,
        description="Vermuk status to set"
    )
    validate_existence: bool = Field(
        True,
        description="Validate all IDs exist before update"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [1, 2, 3, 4, 5],
                "vermuk": True,
                "validate_existence": True
            }
        }
    )

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v: List[int]) -> List[int]:
        """Validate channel IDs."""
        if not v:
            raise ValueError('IDs list cannot be empty')
        if len(v) > 1000:
            raise ValueError('Maximum 1000 IDs allowed')
        unique_ids = list(set(v))
        if len(unique_ids) != len(v):
            raise ValueError('Duplicate IDs detected')
        if any(id < 1 for id in v):
            raise ValueError('Invalid channel ID (must be positive integer)')
        return unique_ids


class ChannelBulkNotes(BaseModel):
    """Schema untuk bulk update notes channel."""
    updates: Dict[int, str] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Mapping of channel_id -> new_notes"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "updates": {
                    1: "Updated note for channel 1",
                    2: "Updated note for channel 2"
                }
            }
        }
    )

    @field_validator('updates')
    @classmethod
    def validate_updates(cls, v: Dict[int, str]) -> Dict[int, str]:
        """Validate updates dict."""
        if not v:
            raise ValueError('Updates dictionary cannot be empty')
        if len(v) > 1000:
            raise ValueError('Maximum 1000 updates allowed')
        
        validated = {}
        for channel_id, notes in v.items():
            if not isinstance(channel_id, int) or channel_id < 1:
                raise ValueError(f'Invalid channel ID: {channel_id}')
            
            if notes is not None:
                notes = notes.strip()
                if len(notes) > 10000:
                    raise ValueError(f'Notes for channel {channel_id} exceeds 10000 characters')
            validated[channel_id] = notes or ''
        
        return validated


class ChannelBulkResponse(BaseModel):
    """Response schema untuk bulk operations."""
    success: bool = Field(..., description="Operation success status")
    action: str = Field(..., description="Action performed")
    count: int = Field(..., ge=0, description="Number of items processed")
    details: Dict[str, Any] = Field(..., description="Detailed results")
    total_requested: int = Field(..., ge=0, description="Total items requested")
    timestamp: datetime = Field(..., description="Operation timestamp")


# =====================================================
# STATISTICS SCHEMAS
# =====================================================

class ChannelDashboardStats(BaseModel):
    """Dashboard statistics schema."""
    total_channels: int = Field(0, ge=0, description="Total channels")
    total_vermuk: int = Field(0, ge=0, description="Vermuk channels")
    total_normal: int = Field(0, ge=0, description="Normal channels")
    total_artists: int = Field(0, ge=0, description="Total artists")
    total_songs: int = Field(0, ge=0, description="Total songs")
    uploaded_songs: int = Field(0, ge=0, description="Uploaded songs")
    pending_songs: int = Field(0, ge=0, description="Pending songs")
    takedown_songs: int = Field(0, ge=0, description="Takedown songs")
    channels_with_artists: int = Field(0, ge=0, description="Channels with artists")
    channels_with_songs: int = Field(0, ge=0, description="Channels with songs")
    artists_with_songs: int = Field(0, ge=0, description="Artists with songs")
    avg_artists_per_channel: float = Field(0.0, ge=0, description="Average artists per channel")
    avg_songs_per_channel: float = Field(0.0, ge=0, description="Average songs per channel")
    avg_songs_per_artist: float = Field(0.0, ge=0, description="Average songs per artist")
    utilization_rate: float = Field(0.0, ge=0, le=100, description="Channel utilization rate")
    status_breakdown: Optional[Dict[str, int]] = Field(
        None,
        description="Status breakdown by song status"
    )
    oldest_channel: Optional[datetime] = Field(None, description="Oldest channel creation date")
    newest_channel: Optional[datetime] = Field(None, description="Newest channel creation date")
    oldest_song: Optional[datetime] = Field(None, description="Oldest song creation date")
    newest_song: Optional[datetime] = Field(None, description="Newest song creation date")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_channels": 50,
                "total_vermuk": 10,
                "total_normal": 40,
                "total_artists": 500,
                "total_songs": 2500,
                "uploaded_songs": 2000,
                "pending_songs": 400,
                "takedown_songs": 100,
                "utilization_rate": 85.5,
                "avg_songs_per_channel": 50.0
            }
        }
    )


class ChannelGrowthData(BaseModel):
    """Channel growth data schema."""
    month_label: str = Field(..., description="Month label (YYYY-MM)")
    month: datetime = Field(..., description="Month date")
    new_songs: int = Field(0, ge=0, description="New songs in month")
    new_artists: int = Field(0, ge=0, description="New artists in month")
    cumulative_songs: int = Field(0, ge=0, description="Cumulative songs")
    cumulative_artists: int = Field(0, ge=0, description="Cumulative artists")


class ChannelDailyStats(BaseModel):
    """Daily statistics schema."""
    day: datetime = Field(..., description="Date")
    songs_created: int = Field(0, ge=0, description="Songs created on this day")
    songs_uploaded: int = Field(0, ge=0, description="Songs uploaded on this day")
    songs_pending: int = Field(0, ge=0, description="Songs pending on this day")
    artists_created: int = Field(0, ge=0, description="Artists created on this day")
    channels_created: int = Field(0, ge=0, description="Channels created on this day")


class ChannelComparison(BaseModel):
    """Channel comparison schema."""
    channels: List[Dict[str, Any]] = Field(..., description="Channel data for comparison")
    metrics: Dict[str, Any] = Field(..., description="Comparison metrics")


# =====================================================
# RESPONSE WRAPPERS
# =====================================================

class APIResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = Field(..., description="Response success status")
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Success",
                "data": {"id": 1, "name": "Channel"},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )


class APIErrorResponse(BaseModel):
    """Generic API error response wrapper."""
    success: bool = Field(False, description="Response success status")
    status_code: int = Field(..., description="HTTP status code")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "status_code": 400,
                "error": "Validation failed",
                "details": {"name": "Name already exists"},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    # Enums
    'ChannelSortField',
    'SortDirection',
    'ChannelLevel',
    
    # Base
    'ChannelBase',
    
    # Create/Update
    'ChannelCreate',
    'ChannelUpdate',
    'ChannelNotesUpdate',
    
    # Response
    'ChannelResponse',
    'ChannelListResponse',
    'ChannelStats',
    'ChannelStatusBreakdown',
    'ChannelActivity',
    
    # Filter
    'ChannelFilter',
    'ChannelFilterRequest',
    
    # Bulk
    'ChannelBulkDelete',
    'ChannelBulkVermuk',
    'ChannelBulkNotes',
    'ChannelBulkResponse',
    
    # Statistics
    'ChannelDashboardStats',
    'ChannelGrowthData',
    'ChannelDailyStats',
    'ChannelComparison',
    
    # Wrappers
    'APIResponse',
    'APIErrorResponse',
]