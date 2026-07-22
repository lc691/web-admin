"""
Artist Schema
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# BASE
# =====================================================

class ArtistBase(BaseModel):
    """
    Base Artist Schema.
    """

    channel_id: int = Field(..., gt=0)
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )


# =====================================================
# CREATE
# =====================================================

class ArtistCreate(ArtistBase):
    """
    Schema create artist.
    """

    pass


# =====================================================
# UPDATE
# =====================================================

class ArtistUpdate(ArtistBase):
    """
    Schema update artist.
    """

    pass


# =====================================================
# RESPONSE
# =====================================================

class ArtistResponse(BaseModel):
    """
    Schema response artist.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: int
    channel_name: str | None = None

    name: str

    song_count: int = 0

    created_at: datetime | None = None
    updated_at: datetime | None = None


# =====================================================
# DETAIL
# =====================================================

class ArtistDetail(ArtistResponse):
    """
    Schema detail artist.
    """

    pass


# =====================================================
# LIST
# =====================================================

class ArtistList(BaseModel):
    """
    Schema list artist.
    """

    total: int
    items: list[ArtistResponse]


# =====================================================
# SEARCH
# =====================================================

class ArtistSearch(BaseModel):
    """
    Schema search artist.
    """

    id: int
    name: str


# =====================================================
# BULK DELETE
# =====================================================

class ArtistBulkDelete(BaseModel):
    """
    Schema bulk delete.
    """

    ids: list[int] = Field(
        ...,
        min_length=1,
    )


# =====================================================
# STATISTICS
# =====================================================

class ArtistStatistics(BaseModel):
    """
    Schema statistik artist.
    """

    total_artists: int = 0
    total_songs: int = 0
    active_channels: int = 0


# =====================================================
# DATATABLE
# =====================================================

class ArtistDataTable(BaseModel):
    """
    Schema DataTables Artist.
    """

    draw: int = 0

    recordsTotal: int
    recordsFiltered: int

    data: list[ArtistResponse]