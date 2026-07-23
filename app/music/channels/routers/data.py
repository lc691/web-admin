"""
Channel Data Router - Complete Implementation

API routes untuk data Channel:
- GET /data - DataTable endpoint
- GET /list - List with filters
- GET /options - Filter options
- GET /simple - Simple list for dropdowns
- GET /export - Export data
"""

from fastapi import APIRouter, Depends, Request, Query, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, List
import csv
import io
from datetime import datetime

from app.core.database import get_dict_cursor_dep
from app.core.datatable import DataTable
from app.music.channels.schemas import ChannelFilterRequest
from app.music.services.channels.service import ChannelService
from app.music.services.channels.exceptions import (
    InvalidFilterError,
    InvalidSortError,
    InvalidPaginationError,
    ChannelError,
)
from app.music.channels.presenter import ChannelPresenter

router = APIRouter()


# =====================================================
# DATATABLE
# =====================================================

@router.get("/data")
async def data(
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    """
    DataTable endpoint untuk server-side pagination.
    
    Args:
        request: FastAPI Request object
        db: Database cursor
        
    Returns:
        DataTable response format
    """
    try:
        cursor, _ = db
        
        # Parse DataTable request
        dt = DataTable(request)
        
        # Get data
        rows = ChannelService.datatable(
            cursor,
            dt,
        )
        
        # Get filtered count
        filtered = ChannelService.count_filtered(
            cursor,
            dt,
        )
        
        # Get total count
        result = ChannelService.get_statistics(
            cursor,
            detailed=False,
        )

        total = (
            result.get("data", {}).get("total_channels", 0)
            if result.get("success")
            else 0
        )
        
        # Return DataTable response
        return dt.response(
            data=rows,
            total=total,
            filtered=filtered,
        )
        
    except Exception as e:
        # Return error response
        return {
            "draw": dt.draw if 'dt' in locals() else 0,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": [],
            "error": str(e),
        }


# =====================================================
# LIST CHANNELS (Alternative to DataTable)
# =====================================================

@router.get("/list")
async def list_channels(
    request: Request,
    keyword: Optional[str] = Query(None, description="Search keyword"),
    vermuk: Optional[bool] = Query(None, description="Filter by vermuk"),
    email: Optional[str] = Query(None, description="Filter by email"),
    date_from: Optional[str] = Query(None, description="Date from"),
    date_to: Optional[str] = Query(None, description="Date to"),
    has_artists: Optional[bool] = Query(None, description="Has artists"),
    has_songs: Optional[bool] = Query(None, description="Has songs"),
    min_artists: Optional[int] = Query(None, ge=0, description="Min artists"),
    max_artists: Optional[int] = Query(None, ge=0, description="Max artists"),
    min_songs: Optional[int] = Query(None, ge=0, description="Min songs"),
    max_songs: Optional[int] = Query(None, ge=0, description="Max songs"),
    order_by: str = Query("created_at", description="Sort column"),
    order_dir: str = Query("desc", description="Sort direction"),
    start: int = Query(0, ge=0, description="Offset"),
    length: int = Query(20, ge=1, le=1000, description="Limit"),
    format: str = Query("json", description="Response format: json or csv"),
    db=Depends(get_dict_cursor_dep),
):
    """
    List channels with filters and pagination.
    
    Args:
        request: FastAPI Request object
        keyword: Search keyword
        vermuk: Filter by vermuk
        email: Filter by email
        date_from: Date from
        date_to: Date to
        has_artists: Has artists
        has_songs: Has songs
        min_artists: Minimum artists
        max_artists: Maximum artists
        min_songs: Minimum songs
        max_songs: Maximum songs
        order_by: Sort column
        order_dir: Sort direction
        start: Offset
        length: Limit
        format: Response format (json or csv)
        db: Database cursor
        
    Returns:
        List of channels or CSV export
    """
    try:
        cursor, _ = db
        
        # Get channels
        result = ChannelService.list_channels(
            cursor,
            keyword=keyword,
            vermuk=vermuk,
            email=email,
            date_from=date_from,
            date_to=date_to,
            has_artists=has_artists,
            has_songs=has_songs,
            min_artists=min_artists,
            max_artists=max_artists,
            min_songs=min_songs,
            max_songs=max_songs,
            order_by=order_by,
            order_dir=order_dir,
            start=start,
            length=length,
        )
        
        # Return as CSV if requested
        if format.lower() == "csv":
            return export_channels_csv(result)
        
        return result
        
    except (InvalidFilterError, InvalidSortError, InvalidPaginationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list channels: {str(e)}"
        )


# =====================================================
# SIMPLE LIST (for dropdowns)
# =====================================================

@router.get("/simple")
async def simple_list(
    request: Request,
    search: Optional[str] = Query(None, description="Search by name"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get simple list of channels (id, name) for dropdowns/select.
    
    Args:
        request: FastAPI Request object
        search: Search by name
        db: Database cursor
        
    Returns:
        Simple list of channels
    """
    try:
        cursor, _ = db
        
        from app.music.repositories.channels.repository import ChannelRepository
        
        channels = ChannelRepository.get_simple_list(cursor)
        
        # Filter by search if provided
        if search:
            search_lower = search.lower()
            channels = [
                c for c in channels 
                if search_lower in c.get('name', '').lower()
            ]
        
        return {
            "success": True,
            "data": channels,
            "count": len(channels),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channel list: {str(e)}"
        )


# =====================================================
# FILTER OPTIONS
# =====================================================

@router.get("/options")
async def get_filter_options(
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    """
    Get available filter options for UI.
    
    Args:
        request: FastAPI Request object
        db: Database cursor
        
    Returns:
        Filter options
    """
    try:
        cursor, _ = db
        
        from app.music.repositories.channels.filter import ChannelFilterRepository
        
        options = ChannelFilterRepository.get_filter_options(cursor)
        
        return {
            "success": True,
            "data": options,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get filter options: {str(e)}"
        )


# =====================================================
# EXPORT CHANNELS
# =====================================================

@router.get("/export")
async def export_channels(
    request: Request,
    format: str = Query("csv", description="Export format: csv, json"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    vermuk: Optional[bool] = Query(None, description="Filter by vermuk"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Export channels to CSV or JSON.
    
    Args:
        request: FastAPI Request object
        format: Export format (csv or json)
        keyword: Search keyword
        vermuk: Filter by vermuk
        db: Database cursor
        
    Returns:
        Exported file
    """
    try:
        cursor, _ = db
        
        # Get all channels (limit to 10000 for export)
        result = ChannelService.list_channels(
            cursor,
            keyword=keyword,
            vermuk=vermuk,
            order_by="created_at",
            order_dir="desc",
            start=0,
            length=10000,  # Max 10000 rows for export
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to export channels')
            )
        
        data = result.get('data', {}).get('data', [])
        
        if format.lower() == "json":
            return export_channels_json(data)
        else:
            return export_channels_csv_data(data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export channels: {str(e)}"
        )


# =====================================================
# EXPORT HELPER FUNCTIONS
# =====================================================

def export_channels_csv(result: dict) -> StreamingResponse:
    """
    Export channels as CSV from result.
    """
    data = result.get('data', {}).get('data', [])
    return export_channels_csv_data(data)


def export_channels_csv_data(data: list) -> StreamingResponse:
    """
    Export channels as CSV from data list.
    """
    if not data:
        return StreamingResponse(
            io.StringIO("No data available"),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=channels_empty_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    headers = [
        "ID", "Name", "Email", "Vermuk", "Notes",
        "Total Artists", "Total Songs", "Uploaded Songs", "Pending Songs", "Takedown Songs",
        "Created At", "Updated At"
    ]
    writer.writerow(headers)
    
    # Data rows
    for item in data:
        row = [
            item.get('id', ''),
            item.get('name', ''),
            item.get('email', ''),
            "Yes" if item.get('vermuk') else "No",
            item.get('notes', ''),
            item.get('total_artists', 0),
            item.get('total_songs', 0),
            item.get('uploaded_songs', 0),
            item.get('pending_songs', 0),
            item.get('takedown_songs', 0),
            item.get('created_at', ''),
            item.get('updated_at', ''),
        ]
        writer.writerow(row)
    
    # Create response
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=channels_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


def export_channels_json(data: list) -> JSONResponse:
    """
    Export channels as JSON.
    """
    return JSONResponse(
        content={
            "success": True,
            "data": data,
            "exported_at": datetime.now().isoformat(),
            "count": len(data),
        },
        headers={
            "Content-Disposition": f"attachment; filename=channels_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


# =====================================================
# BULK EXPORT
# =====================================================

@router.post("/export/bulk")
async def bulk_export(
    request: Request,
    ids: List[int],
    format: str = Query("csv", description="Export format: csv, json"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Export specific channels by IDs.
    
    Args:
        request: FastAPI Request object
        ids: List of channel IDs
        format: Export format (csv or json)
        db: Database cursor
        
    Returns:
        Exported file
    """
    try:
        cursor, _ = db
        
        if not ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No channel IDs provided"
            )
        
        # Get channels by IDs
        channels = []
        for channel_id in ids:
            result = ChannelService.get_by_id(cursor, channel_id, include_stats=True)
            if result.get('success'):
                channels.append(result.get('data'))
        
        if format.lower() == "json":
            return export_channels_json(channels)
        else:
            return export_channels_csv_data(channels)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export channels: {str(e)}"
        )


# =====================================================
# CHANNEL TYPES / ENUMS
# =====================================================

@router.get("/enums")
async def get_enums(
    request: Request,
):
    """
    Get enum values for channel fields.
    
    Returns:
        Enum values for dropdowns
    """
    return {
        "success": True,
        "data": {
            "sort_columns": [
                {"value": "id", "label": "ID"},
                {"value": "name", "label": "Name"},
                {"value": "email", "label": "Email"},
                {"value": "created_at", "label": "Created At"},
                {"value": "updated_at", "label": "Updated At"},
                {"value": "artists", "label": "Artists"},
                {"value": "songs", "label": "Songs"},
                {"value": "vermuk", "label": "Vermuk"},
            ],
            "sort_directions": [
                {"value": "asc", "label": "Ascending"},
                {"value": "desc", "label": "Descending"},
            ],
            "statuses": [
                {"value": "all", "label": "All Statuses"},
                {"value": "vermuk", "label": "Vermuk"},
                {"value": "normal", "label": "Normal"},
            ],
            "has_options": [
                {"value": "all", "label": "All"},
                {"value": "yes", "label": "Yes"},
                {"value": "no", "label": "No"},
            ],
        }
    }


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']