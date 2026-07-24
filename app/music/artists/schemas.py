"""
Artist Schema - Complete Implementation

Pydantic schemas untuk Artist dengan:
- Request/Response validation
- Nested schemas untuk statistics
- Bulk operation schemas
- Filter schemas
- Detailed field validations
- Type hints and documentation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
import re


# =====================================================
# ENUMS
# =====================================================

class ArtistSortField(str, Enum):
    """Sort fields untuk Artist."""
    ID = "id"
    NAME = "name"
    CHANNEL = "channel"
    SONG_COUNT = "song_count"
    UPLOADED_SONGS = "uploaded_songs"
    PENDING_SONGS = "pending_songs"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class SortDirection(str, Enum):
    """Sort direction."""
    ASC = "asc"
    DESC = "desc"


# =====================================================
# BASE SCHEMA
# =====================================================

class ArtistBase(BaseModel):
    """
    Base Artist Schema dengan validasi.
    """
    channel_id: int = Field(
        ...,
        gt=0,
        description="ID channel tempat artist berada"
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nama artist (unique per channel, case-insensitive)"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "channel_id": 1,
                "name": "Michael Jackson"
            }
        }
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate artist name."""
        if not v:
            raise ValueError('Nama artist wajib diisi')
        
        v = v.strip()
        
        if len(v) < 2:
            raise ValueError('Nama artist minimal 2 karakter')
        
        if len(v) > 255:
            raise ValueError('Nama artist maksimal 255 karakter')
        
        # Check for invalid characters
        invalid_pattern = re.compile(r"[<>'\"`]")
        if invalid_pattern.search(v):
            raise ValueError('Nama artist mengandung karakter yang tidak diperbolehkan')
        
        # Allow letters, numbers, spaces, hyphens, underscores, dots, parentheses, ampersand
        name_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.()&]+$')
        if not name_pattern.match(v):
            raise ValueError(
                'Nama artist hanya boleh mengandung huruf, angka, spasi, '
                'dan tanda baca dasar (- _ . ( ) &)'
            )
        
        return v

    @field_validator('channel_id')
    @classmethod
    def validate_channel_id(cls, v: int) -> int:
        """Validate channel ID."""
        if v <= 0:
            raise ValueError('Channel ID harus lebih dari 0')
        return v


# =====================================================
# CREATE SCHEMA
# =====================================================

class ArtistCreate(ArtistBase):
    """
    Schema untuk membuat artist.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "channel_id": 1,
                "name": "New Artist"
            }
        }
    )


# =====================================================
# UPDATE SCHEMA
# =====================================================

class ArtistUpdate(BaseModel):
    """
    Schema untuk mengupdate artist.
    Semua field optional untuk partial update.
    """
    channel_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID channel baru"
    )
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Nama baru artist"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "channel_id": 2,
                "name": "Updated Artist Name"
            }
        }
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate artist name."""
        if v is None:
            return v
        
        v = v.strip()
        
        if not v:
            raise ValueError('Nama artist tidak boleh kosong')
        
        if len(v) < 2:
            raise ValueError('Nama artist minimal 2 karakter')
        
        if len(v) > 255:
            raise ValueError('Nama artist maksimal 255 karakter')
        
        invalid_pattern = re.compile(r"[<>'\"`]")
        if invalid_pattern.search(v):
            raise ValueError('Nama artist mengandung karakter yang tidak diperbolehkan')
        
        name_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.()&]+$')
        if not name_pattern.match(v):
            raise ValueError(
                'Nama artist hanya boleh mengandung huruf, angka, spasi, '
                'dan tanda baca dasar (- _ . ( ) &)'
            )
        
        return v

    @field_validator('channel_id')
    @classmethod
    def validate_channel_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate channel ID."""
        if v is not None and v <= 0:
            raise ValueError('Channel ID harus lebih dari 0')
        return v

    @model_validator(mode='after')
    def validate_at_least_one_field(self) -> 'ArtistUpdate':
        """Validate at least one field is provided."""
        if self.channel_id is None and self.name is None:
            raise ValueError('Setidaknya satu field harus diisi untuk update')
        return self


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class ArtistResponse(BaseModel):
    """
    Schema response untuk Artist.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "channel_id": 1,
                "channel_name": "My Channel",
                "name": "Michael Jackson",
                "song_count": 50,
                "uploaded_songs": 40,
                "pending_songs": 8,
                "takedown_songs": 2,
                "song_status": "released",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )

    id: int = Field(..., description="Artist ID")
    channel_id: int = Field(..., description="Channel ID")
    channel_name: Optional[str] = Field(None, description="Channel name")
    channel_vermuk: Optional[bool] = Field(None, description="Channel vermuk status")
    name: str = Field(..., description="Artist name")

    song_count: int = Field(0, ge=0, description="Total songs")
    uploaded_songs: int = Field(0, ge=0, description="Uploaded songs")
    pending_songs: int = Field(0, ge=0, description="Pending songs")
    takedown_songs: int = Field(0, ge=0, description="Takedown songs")

    # Tambahkan ini
    song_status: Optional[str] = Field(
        None,
        description="Latest song status"
    )

    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
class ArtistDetail(ArtistResponse):
    """
    Schema detail artist dengan informasi tambahan.
    """
    first_song_date: Optional[datetime] = Field(None, description="First song date")
    last_song_date: Optional[datetime] = Field(None, description="Last song date")
    upload_rate: Optional[float] = Field(None, ge=0, le=100, description="Upload rate percentage")
    pending_rate: Optional[float] = Field(None, ge=0, le=100, description="Pending rate percentage")
    days_active: int = Field(0, ge=0, description="Days since first song")
    songs_per_day: float = Field(0.0, ge=0, description="Average songs per day")
    status_breakdown: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Song status breakdown"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "channel_id": 1,
                "channel_name": "My Channel",
                "name": "Michael Jackson",
                "song_count": 50,
                "uploaded_songs": 40,
                "pending_songs": 8,
                "takedown_songs": 2,
                "upload_rate": 80.0,
                "pending_rate": 16.0,
                "days_active": 365,
                "songs_per_day": 0.14,
                "first_song_date": "2024-01-01T00:00:00",
                "last_song_date": "2024-12-31T00:00:00",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )


class ArtistList(BaseModel):
    """
    Schema list artist dengan pagination.
    """
    total: int = Field(..., ge=0, description="Total items")
    items: List[ArtistResponse] = Field(..., description="List of artists")


# =====================================================
# SEARCH SCHEMA
# =====================================================

class ArtistSearch(BaseModel):
    """
    Schema search artist.
    """
    id: int = Field(..., description="Artist ID")
    name: str = Field(..., description="Artist name")
    channel_id: Optional[int] = Field(None, description="Channel ID")
    channel_name: Optional[str] = Field(None, description="Channel name")
    song_count: int = Field(0, ge=0, description="Song count")


# =====================================================
# FILTER SCHEMA
# =====================================================

class ArtistFilter(BaseModel):
    """
    Schema filter untuk Artist.
    """
    keyword: Optional[str] = Field(
        None,
        max_length=255,
        description="Search keyword (name, channel name)"
    )
    channel_id: Optional[int] = Field(
        None,
        gt=0,
        description="Filter by channel ID"
    )
    has_songs: Optional[bool] = Field(
        None,
        description="Filter artists with/without songs"
    )
    status: Optional[str] = Field(
        None,
        description="Filter by song status"
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
    date_from: Optional[datetime] = Field(
        None,
        description="Creation date from"
    )
    date_to: Optional[datetime] = Field(
        None,
        description="Creation date to"
    )
    order_by: ArtistSortField = Field(
        ArtistSortField.NAME,
        description="Sort column"
    )
    order_dir: SortDirection = Field(
        SortDirection.ASC,
        description="Sort direction"
    )
    start: int = Field(0, ge=0, description="Pagination offset")
    length: int = Field(20, ge=1, le=1000, description="Pagination limit")

    @field_validator('keyword')
    @classmethod
    def validate_keyword(cls, v: Optional[str]) -> Optional[str]:
        """Validate search keyword."""
        if v is not None:
            v = v.strip()
            if v and len(v) > 255:
                raise ValueError('Keyword maksimal 255 karakter')
        return v


# =====================================================
# BULK OPERATION SCHEMAS
# =====================================================

class ArtistBulkDelete(BaseModel):
    """
    Schema bulk delete artist.
    """
    ids: List[int] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of artist IDs to delete"
    )
    force: bool = Field(
        False,
        description="Force delete even if artist has songs"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [1, 2, 3, 4, 5],
                "force": False
            }
        }
    )

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v: List[int]) -> List[int]:
        """Validate artist IDs."""
        if not v:
            raise ValueError('IDs list cannot be empty')
        
        if len(v) > 1000:
            raise ValueError('Maksimal 1000 IDs dalam satu operasi')
        
        # Remove duplicates
        unique_ids = list(set(v))
        if len(unique_ids) != len(v):
            raise ValueError('Terdapat ID duplikat')
        
        if any(id <= 0 for id in v):
            raise ValueError('ID artist harus lebih dari 0')
        
        return unique_ids


class ArtistBulkUpdateChannel(BaseModel):
    """
    Schema bulk update channel untuk artist.
    """
    ids: List[int] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of artist IDs"
    )
    channel_id: int = Field(
        ...,
        gt=0,
        description="New channel ID"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ids": [1, 2, 3],
                "channel_id": 5
            }
        }
    )

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v: List[int]) -> List[int]:
        """Validate artist IDs."""
        if not v:
            raise ValueError('IDs list cannot be empty')
        
        if len(v) > 1000:
            raise ValueError('Maksimal 1000 IDs dalam satu operasi')
        
        unique_ids = list(set(v))
        if len(unique_ids) != len(v):
            raise ValueError('Terdapat ID duplikat')
        
        if any(id <= 0 for id in v):
            raise ValueError('ID artist harus lebih dari 0')
        
        return unique_ids


class ArtistBulkUpdateNames(BaseModel):
    """
    Schema bulk update names untuk artist.
    """
    updates: Dict[int, str] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Mapping of artist_id -> new_name"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "updates": {
                    1: "New Artist Name 1",
                    2: "New Artist Name 2"
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
            raise ValueError('Maksimal 1000 updates dalam satu operasi')
        
        validated = {}
        for artist_id, name in v.items():
            if not isinstance(artist_id, int) or artist_id <= 0:
                raise ValueError(f'Invalid artist ID: {artist_id}')
            
            name = name.strip()
            if not name:
                raise ValueError(f'Name for artist {artist_id} cannot be empty')
            
            if len(name) < 2:
                raise ValueError(f'Name for artist {artist_id} must be at least 2 characters')
            
            if len(name) > 255:
                raise ValueError(f'Name for artist {artist_id} must be less than 255 characters')
            
            invalid_pattern = re.compile(r"[<>'\"`]")
            if invalid_pattern.search(name):
                raise ValueError(f'Name for artist {artist_id} contains invalid characters')
            
            name_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.()&]+$')
            if not name_pattern.match(name):
                raise ValueError(
                    f'Name for artist {artist_id} contains invalid characters. '
                    'Allowed: letters, numbers, spaces, hyphens, underscores, dots, parentheses, ampersand'
                )
            
            validated[artist_id] = name
        
        return validated


class ArtistBulkInsert(BaseModel):
    """
    Schema bulk insert artist.
    """
    artists: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of artist data (channel_id, name)"
    )
    skip_duplicates: bool = Field(
        True,
        description="Skip duplicates instead of failing"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "artists": [
                    {"channel_id": 1, "name": "Artist A"},
                    {"channel_id": 1, "name": "Artist B"},
                    {"channel_id": 2, "name": "Artist C"}
                ],
                "skip_duplicates": True
            }
        }
    )

    @field_validator('artists')
    @classmethod
    def validate_artists(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate artists list."""
        if not v:
            raise ValueError('Artists list cannot be empty')
        
        if len(v) > 1000:
            raise ValueError('Maksimal 1000 artist dalam satu operasi')
        
        for idx, artist in enumerate(v):
            if 'channel_id' not in artist:
                raise ValueError(f'Artist at index {idx} missing channel_id')
            
            if 'name' not in artist:
                raise ValueError(f'Artist at index {idx} missing name')
            
            channel_id = artist.get('channel_id')
            if not isinstance(channel_id, int) or channel_id <= 0:
                raise ValueError(f'Invalid channel_id for artist at index {idx}')
            
            name = artist.get('name', '').strip()
            if not name:
                raise ValueError(f'Empty name for artist at index {idx}')
            
            if len(name) < 2:
                raise ValueError(f'Name for artist at index {idx} must be at least 2 characters')
            
            if len(name) > 255:
                raise ValueError(f'Name for artist at index {idx} must be less than 255 characters')
        
        return v


class ArtistBulkResponse(BaseModel):
    """
    Response schema untuk bulk operations.
    """
    success: bool = Field(..., description="Operation success status")
    action: str = Field(..., description="Action performed")
    count: int = Field(0, ge=0, description="Number of items processed")
    details: Dict[str, Any] = Field(..., description="Detailed results")
    total_requested: int = Field(0, ge=0, description="Total items requested")
    timestamp: datetime = Field(..., description="Operation timestamp")


# =====================================================
# API RESPONSE WRAPPERS
# =====================================================

class APIResponse(BaseModel):
    """
    Generic API response wrapper untuk success responses.
    """
    success: bool = Field(True, description="Response success status")
    status_code: int = Field(200, description="HTTP status code")
    message: str = Field("Success", description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Artist retrieved successfully",
                "data": {
                    "id": 1,
                    "name": "Michael Jackson",
                    "channel_id": 1,
                    "channel_name": "My Channel",
                    "song_count": 50
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )


class APIErrorResponse(BaseModel):
    """
    Generic API error response wrapper.
    """
    success: bool = Field(False, description="Response success status")
    status_code: int = Field(..., description="HTTP status code")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "status_code": 400,
                "error": "ValidationError",
                "message": "Invalid artist name",
                "details": {
                    "name": "Artist name must be at least 2 characters"
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )


class APIListResponse(BaseModel):
    """
    API response wrapper for list endpoints.
    """
    success: bool = Field(True, description="Response success status")
    status_code: int = Field(200, description="HTTP status code")
    message: str = Field("Success", description="Response message")
    data: List[Any] = Field(..., description="Response data list")
    count: int = Field(0, ge=0, description="Number of items")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Artists retrieved successfully",
                "data": [
                    {"id": 1, "name": "Artist 1"},
                    {"id": 2, "name": "Artist 2"}
                ],
                "count": 2,
                "meta": {
                    "total": 50,
                    "page": 1,
                    "total_pages": 5
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )


class APIBulkResponse(BaseModel):
    """
    API response wrapper for bulk operations.
    """
    success: bool = Field(True, description="Response success status")
    status_code: int = Field(200, description="HTTP status code")
    message: str = Field("Success", description="Response message")
    data: Dict[str, Any] = Field(..., description="Bulk operation results")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "status_code": 200,
                "message": "3 artists deleted successfully",
                "data": {
                    "deleted_count": 3,
                    "deleted_ids": [1, 2, 3],
                    "not_found": [],
                    "artists_with_songs": []
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )

# =====================================================
# STATISTICS SCHEMA
# =====================================================

class ArtistStatistics(BaseModel):
    """
    Schema statistik artist.
    """
    total_artists: int = Field(0, ge=0, description="Total artists")
    total_songs: int = Field(0, ge=0, description="Total songs")
    active_channels: int = Field(0, ge=0, description="Active channels")
    artists_with_songs: int = Field(0, ge=0, description="Artists with at least one song")
    artists_without_songs: int = Field(0, ge=0, description="Artists with no songs")
    avg_songs_per_artist: float = Field(0.0, ge=0, description="Average songs per artist")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_artists": 100,
                "total_songs": 2500,
                "active_channels": 10,
                "artists_with_songs": 85,
                "artists_without_songs": 15,
                "avg_songs_per_artist": 25.0
            }
        }
    )


class ArtistChannelSummary(BaseModel):
    """
    Schema summary channel untuk artist.
    """
    total_artists: int = Field(0, ge=0, description="Total artists in channel")
    total_songs: int = Field(0, ge=0, description="Total songs in channel")
    artists_with_songs: int = Field(0, ge=0, description="Artists with songs")
    artists_without_songs: int = Field(0, ge=0, description="Artists without songs")
    avg_songs_per_artist: float = Field(0.0, ge=0, description="Average songs per artist")
    oldest_artist: Optional[datetime] = Field(None, description="Oldest artist creation date")
    newest_artist: Optional[datetime] = Field(None, description="Newest artist creation date")


# =====================================================
# DATATABLE SCHEMA
# =====================================================

class ArtistDataTable(BaseModel):
    """
    Schema DataTables Artist.
    """
    draw: int = Field(0, description="DataTable draw counter")
    recordsTotal: int = Field(..., ge=0, description="Total records")
    recordsFiltered: int = Field(..., ge=0, description="Filtered records")
    data: List[ArtistResponse] = Field(..., description="Data rows")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "draw": 1,
                "recordsTotal": 100,
                "recordsFiltered": 50,
                "data": [
                    {
                        "id": 1,
                        "name": "Michael Jackson",
                        "channel_id": 1,
                        "channel_name": "My Channel",
                        "song_count": 50
                    }
                ]
            }
        }
    )


# =====================================================
# CHANNEL SCHEMA
# =====================================================

class ArtistChannel(BaseModel):
    """
    Schema untuk channel dropdown.
    """
    id: int = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "My Channel"
            }
        }
    )


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    # Enums
    'ArtistSortField',
    'SortDirection',
    
    # Base
    'ArtistBase',
    
    # Create/Update
    'ArtistCreate',
    'ArtistUpdate',
    
    # Response
    'ArtistResponse',
    'ArtistDetail',
    'ArtistList',
    
    # Search
    'ArtistSearch',
    
    # Filter
    'ArtistFilter',
    
    # Bulk
    'ArtistBulkDelete',
    'ArtistBulkUpdateChannel',
    'ArtistBulkUpdateNames',
    'ArtistBulkInsert',
    'ArtistBulkResponse',
    
    # Statistics
    'ArtistStatistics',
    'ArtistChannelSummary',
    
    # DataTable
    'ArtistDataTable',
    
    # Channel
    'ArtistChannel',
]