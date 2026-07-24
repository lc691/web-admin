"""
Artist Data Router - Complete Implementation

API routes untuk data Artist:
- GET /data - DataTable endpoint
- GET /list - List with filters
- GET /search - Search artists
- GET /channels - Channel dropdown
- GET /simple - Simple list for dropdowns
- GET /options - Filter options
- GET /export - Export data
- GET /statistics - Statistics
- GET /top - Top artists
- POST /bulk/exists - Bulk existence check
"""

import csv
import io
from datetime import datetime
from typing import List, Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status as http_status,
)
from fastapi.responses import StreamingResponse

from app.music.constants.status import VALID_STATUS
from app.music.artists.schemas import (
    ArtistDataTable,
    ArtistSearch,
    ArtistStatistics,
)
from app.music.services.artists.service import ArtistService
from app.music.services.artists.exceptions import (
    ArtistDatabaseError,
    ChannelNotFoundError,
    InvalidFilterError,
    InvalidSortError,
    InvalidArtistStatusError,
)

router = APIRouter()


# =====================================================
# DATATABLE
# =====================================================

@router.get(
    "/data",
    response_model=ArtistDataTable,
    summary="DataTable endpoint",
    description="Server-side DataTable endpoint untuk artists",
)
def datatable(
    draw: int = Query(0, description="DataTable draw counter"),
    start: int = Query(0, ge=0, description="Pagination offset"),
    length: int = Query(10, ge=1, le=1000, description="Pagination limit"),
    search: str = Query("", description="Search keyword"),
    channel_id: Optional[int] = Query(
        None,
        ge=1,
        description="Filter by channel ID",
    ),
    has_songs: Optional[bool] = Query(
        None,
        description="Filter artists with/without songs",
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by song status",
    ),
    order_column: int = Query(
        1,
        ge=0,
        le=8,
        description="Sort column index",
    ),
    order_dir: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Sort direction",
    ),
):
    """
    DataTables Artist.

    status = Song Status
    (draft, review, approved, scheduled,
     unreleased, released, live, topic,
     no_ads, take_down)
    """

    try:
        return ArtistService.datatable(
            draw=draw,
            start=start,
            length=length,
            search=search,
            channel_id=channel_id,
            has_songs=has_songs,
            status=status,
            order_column=order_column,
            order_dir=order_dir,
        )

    except InvalidArtistStatusError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail={
                "message": str(exc),
                "code": getattr(exc, "code", "INVALID_ARTIST_STATUS"),
                "details": getattr(exc, "details", {}),
            },
        )

    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": str(exc),
                "code": getattr(exc, "code", "DATABASE_ERROR"),
                "details": getattr(exc, "details", {}),
            },
        )

    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Failed to load artists: {exc}",
                "code": "INTERNAL_SERVER_ERROR",
            },
        )

# =====================================================
# LIST
# =====================================================

@router.get(
    "/list",
    summary="List artists",
    description="List artists with filters and pagination"
)
def list_artists(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
    has_songs: Optional[bool] = Query(None, description="Filter by songs existence"),
    status: Optional[str] = Query(None, description="Filter by song status"),
    min_songs: Optional[int] = Query(None, ge=0, description="Minimum songs"),
    max_songs: Optional[int] = Query(None, ge=0, description="Maximum songs"),
    date_from: Optional[str] = Query(None, description="Date from"),
    date_to: Optional[str] = Query(None, description="Date to"),
    order_by: str = Query("name", description="Sort column"),
    order_dir: str = Query("asc", description="Sort direction"),
    start: int = Query(0, ge=0, description="Pagination offset"),
    length: int = Query(20, ge=1, le=1000, description="Pagination limit"),
):
    """
    List artists with advanced filtering.
    
    Returns:
        List of artists with metadata
    """
    try:
        result = ArtistService.filter_artists(
            keyword=keyword,
            channel_id=channel_id,
            has_songs=has_songs,
            status=status,
            min_songs=min_songs,
            max_songs=max_songs,
            date_from=date_from,
            date_to=date_to,
            order_by=order_by,
            order_dir=order_dir,
            start=start,
            length=length,
        )
        
        return {
            "success": True,
            "data": result.get('data', []),
            "meta": result.get('meta', {}),
        }

    except (InvalidFilterError, InvalidSortError) as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list artists: {str(exc)}"
        )


# =====================================================
# SEARCH
# =====================================================

@router.get(
    "/search",
    response_model=List[ArtistSearch],
    summary="Search artists",
    description="Search artists by keyword"
)
def search(
    keyword: str = Query(..., min_length=1, max_length=255, description="Search keyword"),
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
):
    """
    Search artists by keyword.
    
    Args:
        keyword: Search keyword
        channel_id: Optional channel filter
        limit: Max results
        
    Returns:
        List of matching artists
    """
    try:
        results = ArtistService.search(
            keyword=keyword,
            channel_id=channel_id,
            limit=limit,
        )
        return results

    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search: {str(exc)}"
        )


# =====================================================
# SIMPLE LIST
# =====================================================

@router.get(
    "/simple",
    summary="Simple artist list",
    description="Get simple list of artists for dropdowns"
)
def simple_list(
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
):
    """
    Get simple list of artists (id, name) for dropdowns.
    
    Args:
        channel_id: Optional channel filter
        
    Returns:
        Simple list of artists
    """
    try:
        from app.music.repositories.artists.repository import ArtistRepository
        from app.core.database import get_dict_cursor
        
        with get_dict_cursor() as (cursor, conn):
            artists = ArtistRepository.get_simple_list(cursor, channel_id)
        
        return {
            "success": True,
            "data": artists,
            "count": len(artists),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get artist list: {str(exc)}"
        )


# =====================================================
# CHANNELS
# =====================================================

@router.get(
    "/channels",
    summary="Channel dropdown",
    description="Get channels for dropdown"
)
def channels():
    """
    Dropdown Channel untuk form.
    
    Returns:
        List of channels
    """
    try:
        return ArtistService.get_channels()

    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channels: {str(exc)}"
        )


# =====================================================
# FILTER OPTIONS
# =====================================================

@router.get(
    "/options",
    summary="Filter options",
    description="Get available filter options for UI"
)
def filter_options():
    """
    Get filter options for UI.
    
    Returns:
        Filter options
    """
    try:
        from app.music.repositories.artists.filter import ArtistFilterRepository
        from app.core.database import get_dict_cursor
        
        with get_dict_cursor() as (cursor, conn):
            options = ArtistFilterRepository.get_filter_options(cursor)
        
        return {
            "success": True,
            "data": options,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get filter options: {str(exc)}"
        )


# =====================================================
# STATISTICS
# =====================================================

@router.get(
    "/statistics",
    response_model=ArtistStatistics,
    summary="Artist statistics",
    description="Get artist statistics"
)
def statistics(
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
    detailed: bool = Query(False, description="Get detailed statistics"),
):
    """
    Get artist statistics.
    
    Args:
        channel_id: Optional channel filter
        detailed: Get detailed statistics
        
    Returns:
        Statistics data
    """
    try:
        return ArtistService.statistics(
            channel_id=channel_id,
            detailed=detailed,
        )

    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(exc)}"
        )


# =====================================================
# TOP ARTISTS
# =====================================================

@router.get(
    "/top",
    summary="Top artists",
    description="Get top artists by song count"
)
def top_artists(
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
    limit: int = Query(10, ge=1, le=100, description="Number of artists"),
    min_songs: int = Query(1, ge=0, description="Minimum songs"),
):
    """
    Get top artists by song count.
    
    Args:
        channel_id: Optional channel filter
        limit: Number of artists
        min_songs: Minimum songs
        
    Returns:
        List of top artists
    """
    try:
        artists = ArtistService.top_artists(
            channel_id=channel_id,
            limit=limit,
            min_songs=min_songs,
        )
        
        return {
            "success": True,
            "data": artists,
            "count": len(artists),
        }

    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top artists: {str(exc)}"
        )


# =====================================================
# BULK EXISTS
# =====================================================

@router.post(
    "/bulk/exists",
    summary="Bulk existence check",
    description="Check if multiple artist IDs exist"
)
def bulk_exists(
    artist_ids: List[int],
):
    """
    Check existence of multiple artists.
    
    Args:
        artist_ids: List of artist IDs
        
    Returns:
        Dict mapping ID -> exists
    """
    try:
        result = ArtistService.bulk_exists(artist_ids)
        
        return {
            "success": True,
            "data": result,
            "existing": [id for id, exists in result.items() if exists],
            "not_found": [id for id, exists in result.items() if not exists],
        }

    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check existence: {str(exc)}"
        )


# =====================================================
# EXPORT
# =====================================================

@router.get(
    "/export",
    summary="Export artists",
    description="Export artists by channel"
)
def export_artists(
    channel_id: int = Query(..., ge=1, description="Channel ID"),
    format: str = Query("json", description="Export format: json or csv"),
):
    """
    Export artists by channel.
    
    Args:
        channel_id: Channel ID
        format: Export format (json or csv)
        
    Returns:
        Exported data
    """
    try:
        data = ArtistService.export_by_channel(
            channel_id=channel_id,
            format=format,
        )
        
        if format.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            headers = ["ID", "Name", "Song Count", "Uploaded Songs", "Pending Songs", "Created At", "Updated At"]
            writer.writerow(headers)
            
            # Data rows
            for artist in data:
                row = [
                    artist.get('id', ''),
                    artist.get('name', ''),
                    artist.get('song_count', 0),
                    artist.get('uploaded_songs', 0),
                    artist.get('pending_songs', 0),
                    artist.get('created_at', ''),
                    artist.get('updated_at', ''),
                ]
                writer.writerow(row)
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=artists_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
        }

    except ChannelNotFoundError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export: {str(exc)}"
        )


# =====================================================
# CHANNEL ARTISTS
# =====================================================

@router.get(
    "/channel/{channel_id}",
    summary="Get artists by channel",
    description="Get all artists in a channel"
)
def get_channel_artists(
    channel_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Max records"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: Optional[str] = Query(None, description="Search keyword"),
):
    """
    Get artists by channel.
    
    Args:
        channel_id: Channel ID
        limit: Max records
        offset: Pagination offset
        search: Search keyword
        
    Returns:
        List of artists
    """
    try:
        artists = ArtistService.get_by_channel(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            search=search,
        )
        
        return {
            "success": True,
            "data": artists,
            "count": len(artists),
            "channel_id": channel_id,
        }

    except ChannelNotFoundError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    except ArtistDatabaseError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channel artists: {str(exc)}"
        )


__all__ = ['router']