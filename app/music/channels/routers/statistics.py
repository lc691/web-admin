"""
Channel Statistics Router - Complete Implementation

API routes untuk statistics Channel:
- GET /statistics - Dashboard statistics
- GET /statistics/summary - Simple summary statistics
- GET /statistics/channel/{id} - Channel specific statistics
- GET /statistics/activity/{id} - Activity score
- GET /statistics/status-breakdown - Status breakdown
- GET /statistics/top-channels - Top channels
- GET /statistics/top-artists - Top artists
- GET /statistics/daily - Daily statistics
- GET /statistics/growth/{id} - Growth data
- POST /statistics/compare - Compare channels
- GET /statistics/metrics - Real-time metrics
- POST /statistics/bulk-status - Bulk status breakdown
- GET /statistics/export - Export statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
import csv
import io

from app.core.database import get_dict_cursor_dep
from app.music.services.channels.service import ChannelService
from app.music.services.channels.exceptions import (
    ChannelNotFoundError,
    ChannelError,
)
from app.music.channels.schemas import (
    ChannelDashboardStats,
    ChannelStats,
    ChannelActivity,
    ChannelGrowthData,
    ChannelDailyStats,
    ChannelComparison,
    APIResponse,
    APIErrorResponse,
)

router = APIRouter()


# =====================================================
# DASHBOARD STATISTICS
# =====================================================

@router.get(
    "/statistics",
    response_model=APIResponse,
    summary="Get dashboard statistics",
    description="Get comprehensive dashboard statistics for channels"
)
async def get_statistics(
    detailed: bool = Query(False, description="Get detailed statistics with breakdowns"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get dashboard statistics for channels.
    
    Args:
        detailed: Get detailed statistics with breakdowns
        db: Database cursor
        
    Returns:
        Dashboard statistics
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_statistics(cursor, detailed=detailed)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to get statistics')
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


# =====================================================
# SIMPLE STATISTICS (Quick summary)
# =====================================================

@router.get(
    "/statistics/summary",
    response_model=APIResponse,
    summary="Get simple summary statistics",
    description="Get simple summary statistics (faster, less detailed)"
)
async def get_summary_statistics(
    db=Depends(get_dict_cursor_dep),
):
    """
    Get simple summary statistics (faster, less detailed).
    
    Args:
        db: Database cursor
        
    Returns:
        Simple summary statistics
    """
    try:
        cursor, conn = db
        
        # Use simple summary from statistics repository
        from app.music.repositories.channels.statistics import ChannelStatisticsRepository
        
        stats = ChannelStatisticsRepository.summary_simple(cursor)
        
        return {
            "success": True,
            "status_code": 200,
            "data": stats,
            "message": "Summary statistics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary statistics: {str(e)}"
        )


# =====================================================
# CHANNEL SPECIFIC STATISTICS
# =====================================================

@router.get(
    "/statistics/channel/{channel_id}",
    response_model=APIResponse,
    summary="Get channel statistics",
    description="Get detailed statistics for a specific channel"
)
async def get_channel_statistics(
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    """
    Get detailed statistics for a specific channel.
    
    Args:
        channel_id: Channel ID
        db: Database cursor
        
    Returns:
        Channel statistics
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_channel_stats(cursor, channel_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Channel not found')
            )
        
        return result
        
    except ChannelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channel statistics: {str(e)}"
        )


# =====================================================
# ACTIVITY SCORE
# =====================================================

@router.get(
    "/statistics/activity/{channel_id}",
    response_model=APIResponse,
    summary="Get channel activity score",
    description="Get activity scoring for a channel"
)
async def get_channel_activity(
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    """
    Get activity score for a channel.
    
    Args:
        channel_id: Channel ID
        db: Database cursor
        
    Returns:
        Activity score data
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_activity_score(cursor, channel_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Channel not found')
            )
        
        return result
        
    except ChannelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity score: {str(e)}"
        )


# =====================================================
# STATUS BREAKDOWN
# =====================================================

@router.get(
    "/statistics/status-breakdown",
    response_model=APIResponse,
    summary="Get status breakdown",
    description="Get status breakdown for all channels or a specific channel"
)
async def get_status_breakdown(
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get status breakdown for all channels or a specific channel.
    
    Args:
        channel_id: Optional channel ID filter
        db: Database cursor
        
    Returns:
        Status breakdown data
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_status_breakdown(cursor, channel_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to get status breakdown')
            )
        
        return result
        
    except ChannelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status breakdown: {str(e)}"
        )


# =====================================================
# TOP CHANNELS
# =====================================================

@router.get(
    "/statistics/top-channels",
    response_model=APIResponse,
    summary="Get top channels",
    description="Get top channels by song count"
)
async def get_top_channels(
    limit: int = Query(10, ge=1, le=100, description="Number of channels to return"),
    min_songs: int = Query(1, ge=0, description="Minimum songs filter"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get top channels by song count.
    
    Args:
        limit: Number of channels to return
        min_songs: Minimum songs filter
        db: Database cursor
        
    Returns:
        Top channels
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_top_channels(cursor, limit=limit, min_songs=min_songs)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to get top channels')
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top channels: {str(e)}"
        )


# =====================================================
# TOP ARTISTS
# =====================================================

@router.get(
    "/statistics/top-artists",
    response_model=APIResponse,
    summary="Get top artists",
    description="Get top artists by song count"
)
async def get_top_artists(
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    limit: int = Query(10, ge=1, le=100, description="Number of artists to return"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get top artists by song count.
    
    Args:
        channel_id: Optional channel ID filter
        limit: Number of artists to return
        db: Database cursor
        
    Returns:
        Top artists
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_top_artists(cursor, channel_id=channel_id, limit=limit)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to get top artists')
            )
        
        return result
        
    except ChannelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top artists: {str(e)}"
        )


# =====================================================
# DAILY STATISTICS
# =====================================================

@router.get(
    "/statistics/daily",
    response_model=APIResponse,
    summary="Get daily statistics",
    description="Get daily statistics for channels"
)
async def get_daily_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    channel_id: Optional[int] = Query(None, description="Filter by channel ID"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get daily statistics for channels.
    
    Args:
        days: Number of days to look back
        channel_id: Optional channel ID filter
        db: Database cursor
        
    Returns:
        Daily statistics
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_daily_stats(cursor, days=days, channel_id=channel_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to get daily statistics')
            )
        
        return result
        
    except ChannelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get daily statistics: {str(e)}"
        )


# =====================================================
# GROWTH DATA
# =====================================================

@router.get(
    "/statistics/growth/{channel_id}",
    response_model=APIResponse,
    summary="Get channel growth data",
    description="Get monthly growth data for a channel"
)
async def get_growth_data(
    channel_id: int,
    months: int = Query(12, ge=1, le=36, description="Number of months to look back"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get channel growth data.
    
    Args:
        channel_id: Channel ID
        months: Number of months to look back
        db: Database cursor
        
    Returns:
        Growth data
    """
    try:
        cursor, conn = db
        
        result = ChannelService.get_growth_data(cursor, channel_id=channel_id, months=months)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Channel not found or no data')
            )
        
        return result
        
    except ChannelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get growth data: {str(e)}"
        )


# =====================================================
# COMPARE CHANNELS
# =====================================================

@router.post(
    "/statistics/compare",
    response_model=APIResponse,
    summary="Compare channels",
    description="Compare multiple channels side by side"
)
async def compare_channels(
    channel_ids: List[int],
    db=Depends(get_dict_cursor_dep),
):
    """
    Compare multiple channels.
    
    Args:
        channel_ids: List of channel IDs to compare
        db: Database cursor
        
    Returns:
        Comparison data
    """
    try:
        cursor, conn = db
        
        if not channel_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No channel IDs provided"
            )
        
        if len(channel_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 channels required for comparison"
            )
        
        result = ChannelService.compare_channels(cursor, channel_ids)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to compare channels')
            )
        
        return result
        
    except ChannelNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare channels: {str(e)}"
        )


# =====================================================
# CHANNEL METRICS (Real-time dashboard)
# =====================================================

@router.get(
    "/statistics/metrics",
    summary="Get real-time channel metrics",
    description="Get real-time channel metrics for dashboard"
)
async def get_channel_metrics(
    db=Depends(get_dict_cursor_dep),
):
    """
    Get real-time channel metrics for dashboard.
    
    Args:
        db: Database cursor
        
    Returns:
        Channel metrics
    """
    try:
        cursor, conn = db
        
        # Get basic counts
        from app.music.repositories.channels.statistics import ChannelStatisticsRepository
        
        total_channels = ChannelStatisticsRepository.total_channels(cursor)
        total_artists = ChannelStatisticsRepository.total_artists(cursor)
        total_songs = ChannelStatisticsRepository.total_songs(cursor)
        total_vermuk = ChannelStatisticsRepository.total_vermuk(cursor)
        total_normal = ChannelStatisticsRepository.total_normal(cursor)
        
        # Get recent activity (last 7 days)
        from datetime import datetime, timedelta
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM channels
            WHERE created_at >= %s
        """, (datetime.now() - timedelta(days=7),))
        new_channels_7d = cursor.fetchone()['count'] if cursor.description else 0
        
        # Get active channels (with songs in last 30 days)
        cursor.execute("""
            SELECT COUNT(DISTINCT c.id) as count
            FROM channels c
            JOIN artists a ON a.channel_id = c.id
            JOIN songs s ON s.artist_id = a.id
            WHERE s.created_at >= %s
        """, (datetime.now() - timedelta(days=30),))
        active_channels = cursor.fetchone()['count'] if cursor.description else 0
        
        return {
            "success": True,
            "status_code": 200,
            "data": {
                "total_channels": total_channels,
                "total_artists": total_artists,
                "total_songs": total_songs,
                "total_vermuk": total_vermuk,
                "total_normal": total_normal,
                "new_channels_7d": new_channels_7d,
                "active_channels_30d": active_channels,
                "utilization_rate": round(
                    (active_channels / total_channels * 100) if total_channels > 0 else 0,
                    2
                ),
                "timestamp": datetime.now().isoformat(),
            },
            "message": "Channel metrics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channel metrics: {str(e)}"
        )


# =====================================================
# BULK STATUS BREAKDOWN
# =====================================================

@router.post(
    "/statistics/bulk-status",
    summary="Get bulk status breakdown",
    description="Get status breakdown for multiple channels"
)
async def get_bulk_status_breakdown(
    channel_ids: List[int],
    db=Depends(get_dict_cursor_dep),
):
    """
    Get status breakdown for multiple channels.
    
    Args:
        channel_ids: List of channel IDs
        db: Database cursor
        
    Returns:
        Status breakdown for each channel
    """
    try:
        cursor, conn = db
        
        if not channel_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No channel IDs provided"
            )
        
        result = {}
        for channel_id in channel_ids:
            try:
                stats = ChannelService.get_channel_stats(cursor, channel_id)
                if stats.get('success'):
                    result[channel_id] = stats.get('data', {})
            except Exception as e:
                result[channel_id] = {'error': str(e)}
        
        return {
            "success": True,
            "status_code": 200,
            "data": result,
            "message": f"Status breakdown for {len(result)} channels retrieved"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bulk status breakdown: {str(e)}"
        )


# =====================================================
# EXPORT STATISTICS
# =====================================================

@router.get(
    "/statistics/export",
    summary="Export statistics",
    description="Export statistics data in CSV or JSON format"
)
async def export_statistics(
    format: str = Query("json", description="Export format: json or csv"),
    period: str = Query("monthly", description="Period: daily, weekly, monthly"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Export statistics data.
    
    Args:
        format: Export format (json or csv)
        period: Period for data
        db: Database cursor
        
    Returns:
        Exported statistics
    """
    try:
        cursor, conn = db
        
        # Get statistics
        result = ChannelService.get_statistics(cursor, detailed=True)
        stats = result.get('data', {}) if result.get('success') else {}
        
        # Get daily stats
        days = 30 if period == "daily" else 90 if period == "weekly" else 365
        daily_result = ChannelService.get_daily_stats(cursor, days=days)
        daily_stats = daily_result.get('data', []) if daily_result.get('success') else []
        
        export_data = {
            "summary": stats,
            "daily": daily_stats,
            "period": period,
            "exported_at": datetime.now().isoformat(),
        }
        
        if format.lower() == "csv":
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Summary headers
            writer.writerow(["Metric", "Value"])
            for key, value in stats.items():
                if isinstance(value, (int, float, str)):
                    writer.writerow([key, value])
            
            writer.writerow([])
            writer.writerow(["Daily Statistics"])
            writer.writerow(["Date", "Songs Created", "Songs Uploaded", "Songs Pending", "Artists Created", "Channels Created"])
            
            for day in daily_stats:
                writer.writerow([
                    day.get('day', ''),
                    day.get('songs_created', 0),
                    day.get('songs_uploaded', 0),
                    day.get('songs_pending', 0),
                    day.get('artists_created', 0),
                    day.get('channels_created', 0),
                ])
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=statistics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
        return {
            "success": True,
            "status_code": 200,
            "data": export_data,
            "message": "Statistics exported successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export statistics: {str(e)}"
        )


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']