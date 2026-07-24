"""
Artist Statistics Router - Complete Implementation

API routes untuk statistics Artist:
- GET /statistics - Dashboard statistics
- GET /statistics/total-artists - Total artists
- GET /statistics/active-channels - Active channels
- GET /statistics/channel/{id} - Channel summary
- GET /statistics/top - Top artists
- GET /statistics/growth - Growth data
- GET /{id}/statistics/songs - Total songs per artist
- GET /{id}/statistics/status - Song status breakdown
- GET /{id}/statistics/detail - Detailed artist stats
- GET /statistics/export - Export statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, List
import csv
import io
from datetime import datetime

from app.music.artists.schemas import (
    ArtistStatistics,
    ArtistChannelSummary,
    ArtistDetail,
)
from app.music.services.artists.service import ArtistService
from app.music.services.artists.exceptions import (
    ArtistDatabaseError,
    ArtistNotFoundError,
    ChannelNotFoundError,
)

router = APIRouter()


# =====================================================
# DASHBOARD STATISTICS
# =====================================================

@router.get(
    "/statistics",
    response_model=ArtistStatistics,
    summary="Artist dashboard statistics",
    description="Get comprehensive artist statistics"
)
def statistics(
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
    detailed: bool = Query(False, description="Get detailed statistics"),
):
    """
    Dashboard statistik artist.
    
    Args:
        channel_id: Optional channel filter
        detailed: Get detailed statistics
        
    Returns:
        Statistics data
    """
    try:
        result = ArtistService.statistics(
            channel_id=channel_id,
            detailed=detailed,
        )
        
        return result

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# TOTAL ARTISTS
# =====================================================

@router.get(
    "/statistics/total-artists",
    summary="Total artists",
    description="Get total number of artists"
)
def total_artists(
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
):
    """
    Total artist.
    
    Args:
        channel_id: Optional channel filter
        
    Returns:
        Total artists count
    """
    try:
        total = ArtistService.total_artists(channel_id)
        
        return {
            "success": True,
            "data": {
                "total": total,
                "channel_id": channel_id,
            }
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# ACTIVE CHANNELS
# =====================================================

@router.get(
    "/statistics/active-channels",
    summary="Active channels",
    description="Get number of channels that have artists"
)
def active_channels():
    """
    Channel yang memiliki artist.
    
    Returns:
        Active channels count
    """
    try:
        total = ArtistService.active_channels()
        
        return {
            "success": True,
            "data": {
                "total": total,
            }
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# CHANNEL SUMMARY
# =====================================================

@router.get(
    "/statistics/channel/{channel_id}",
    response_model=ArtistChannelSummary,
    summary="Channel summary",
    description="Get artist summary for a specific channel"
)
def channel_summary(
    channel_id: int,
):
    """
    Ringkasan artist per channel.
    
    Args:
        channel_id: Channel ID
        
    Returns:
        Channel summary data
    """
    try:
        return ArtistService.channel_summary(channel_id)

    except ChannelNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Channel not found",
                "message": str(exc),
                "channel_id": channel_id,
            },
        )
    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# TOP ARTISTS
# =====================================================

@router.get(
    "/statistics/top",
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
            "channel_id": channel_id,
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# ARTIST TOTAL SONGS
# =====================================================

@router.get(
    "/{artist_id}/statistics/songs",
    summary="Artist total songs",
    description="Get total songs for an artist"
)
def total_songs(
    artist_id: int,
):
    """
    Total lagu artist.
    
    Args:
        artist_id: Artist ID
        
    Returns:
        Total songs count
    """
    try:
        total = ArtistService.total_songs(artist_id)
        
        return {
            "success": True,
            "data": {
                "total": total,
                "artist_id": artist_id,
            }
        }

    except ArtistNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artist not found",
                "message": str(exc),
                "artist_id": artist_id,
            },
        )
    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# ARTIST SONG STATUS
# =====================================================

@router.get(
    "/{artist_id}/statistics/status",
    summary="Artist song status",
    description="Get song status breakdown for an artist"
)
def song_status(
    artist_id: int,
):
    """
    Statistik status lagu.
    
    Args:
        artist_id: Artist ID
        
    Returns:
        Song status breakdown
    """
    try:
        status = ArtistService.song_status(artist_id)
        
        return {
            "success": True,
            "data": status,
            "artist_id": artist_id,
        }

    except ArtistNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artist not found",
                "message": str(exc),
                "artist_id": artist_id,
            },
        )
    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# ARTIST DETAILED STATS
# =====================================================

@router.get(
    "/{artist_id}/statistics/detail",
    response_model=ArtistDetail,
    summary="Artist detailed statistics",
    description="Get detailed statistics for an artist"
)
def artist_detail_stats(
    artist_id: int,
):
    """
    Detailed statistics for an artist.
    
    Args:
        artist_id: Artist ID
        
    Returns:
        Detailed artist statistics
    """
    try:
        # Get artist with stats
        from app.core.database import get_dict_cursor
        from app.music.repositories.artists.statistics import ArtistStatisticsRepository
        
        with get_dict_cursor() as (cursor, conn):
            stats = ArtistStatisticsRepository.artist_detail_stats(cursor, artist_id)
            
            if not stats:
                raise ArtistNotFoundError(artist_id=artist_id)
            
            # Get song status
            status = ArtistStatisticsRepository.song_status(cursor, artist_id)
            
            stats['status_breakdown'] = status
            
            return stats

    except ArtistNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artist not found",
                "message": str(exc),
                "artist_id": artist_id,
            },
        )
    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# GROWTH DATA
# =====================================================

@router.get(
    "/statistics/growth",
    summary="Artist growth data",
    description="Get artist growth data by channel"
)
def growth_data(
    channel_id: Optional[int] = Query(None, ge=1, description="Channel ID"),
    months: int = Query(12, ge=1, le=36, description="Number of months"),
):
    """
    Get artist growth data.
    
    Args:
        channel_id: Optional channel filter
        months: Number of months
        
    Returns:
        Growth data
    """
    try:
        from app.core.database import get_dict_cursor
        from app.music.repositories.artists.statistics import ArtistStatisticsRepository
        
        with get_dict_cursor() as (cursor, conn):
            if channel_id:
                growth = ArtistStatisticsRepository.growth_by_channel(
                    cursor,
                    channel_id=channel_id,
                    months=months,
                )
            else:
                # Get overall growth
                growth = ArtistStatisticsRepository.daily_activity(
                    cursor,
                    days=months * 30,
                )
        
        return {
            "success": True,
            "data": growth,
            "channel_id": channel_id,
            "months": months,
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# COMPARE ARTISTS
# =====================================================

@router.post(
    "/statistics/compare",
    summary="Compare artists",
    description="Compare multiple artists side by side"
)
def compare_artists(
    artist_ids: List[int],
):
    """
    Compare multiple artists.
    
    Args:
        artist_ids: List of artist IDs
        
    Returns:
        Comparison data
    """
    try:
        from app.core.database import get_dict_cursor
        from app.music.repositories.artists.statistics import ArtistStatisticsRepository
        
        with get_dict_cursor() as (cursor, conn):
            comparison = ArtistStatisticsRepository.compare_artists(
                cursor,
                artist_ids=artist_ids,
            )
        
        return {
            "success": True,
            "data": comparison,
            "artist_ids": artist_ids,
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# EXPORT STATISTICS
# =====================================================

@router.get(
    "/statistics/export",
    summary="Export statistics",
    description="Export artist statistics in CSV or JSON format"
)
def export_statistics(
    format: str = Query("json", description="Export format: json or csv"),
    channel_id: Optional[int] = Query(None, ge=1, description="Filter by channel"),
):
    """
    Export artist statistics.
    
    Args:
        format: Export format (json or csv)
        channel_id: Optional channel filter
        
    Returns:
        Exported data
    """
    try:
        stats = ArtistService.statistics(
            channel_id=channel_id,
            detailed=True,
        )
        
        # Get top artists
        top = ArtistService.top_artists(
            channel_id=channel_id,
            limit=20,
        )
        
        export_data = {
            "statistics": stats,
            "top_artists": top,
            "channel_id": channel_id,
            "exported_at": datetime.now().isoformat(),
        }
        
        if format.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Summary
            writer.writerow(["Metric", "Value"])
            for key, value in stats.items():
                writer.writerow([key, value])
            
            writer.writerow([])
            writer.writerow(["Top Artists"])
            writer.writerow(["Rank", "Name", "Song Count", "Uploaded Songs", "Pending Songs"])
            
            for idx, artist in enumerate(top, 1):
                writer.writerow([
                    idx,
                    artist.get('name', ''),
                    artist.get('song_count', 0),
                    artist.get('uploaded_songs', 0),
                    artist.get('pending_songs', 0),
                ])
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=artist_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
        return {
            "success": True,
            "data": export_data,
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Database error",
                "message": str(exc),
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error",
                "message": str(exc),
            },
        )


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']