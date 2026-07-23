"""
Bulk Channel Router - Complete Implementation

API routes untuk bulk operations Channel:
- POST /bulk/delete - Bulk delete channels
- POST /bulk/vermuk - Bulk update vermuk
- POST /bulk/notes - Bulk update notes
- POST /bulk/upsert - Bulk upsert channels
- POST /bulk/import - Bulk import channels
- POST /bulk/export - Bulk export channels
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import csv
import io
from datetime import datetime

from app.core.database import get_dict_cursor_dep_commit, get_dict_cursor_dep
from app.music.channels.schemas import (
    ChannelBulkDelete,
    ChannelBulkVermuk,
    ChannelBulkNotes,
    ChannelBulkResponse,
    APIResponse,
    APIErrorResponse,
)
from app.music.services.channels.exceptions import (
    ChannelError,
    ChannelNotFoundError,
    BulkChannelError,
    BulkValidationError,
    ChannelsNotFoundError,
    InvalidChannelNotesError,
)
from app.music.services.channels.service import ChannelService
from app.music.services.channels.mapper import ChannelMapper

router = APIRouter()


# =====================================================
# BULK DELETE
# =====================================================

@router.post(
    "/delete",
    response_model=APIResponse,
    summary="Bulk delete channels",
    description="Delete multiple channels at once (cascade deletes artists and songs)"
)
async def bulk_delete(
    data: ChannelBulkDelete,
    cursor=Depends(get_dict_cursor_dep_commit),
):
    """
    Bulk delete channels.
    
    Args:
        data: Bulk delete data with IDs
        cursor: Database cursor with commit
        
    Returns:
        Bulk delete result
    """
    try:
        conn = cursor.connection
        
        result = ChannelService.bulk_delete(
            cursor,
            ids=data.ids,
            validate_existence=data.validate_existence,
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Bulk delete failed')
            )
        
        conn.commit()
        
        return result
        
    except ChannelsNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except BulkValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except BulkChannelError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except ChannelError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk delete: {str(exc)}",
        )


# =====================================================
# BULK UPDATE VERMUK
# =====================================================

@router.post(
    "/vermuk",
    response_model=APIResponse,
    summary="Bulk update vermuk",
    description="Update vermuk status for multiple channels"
)
async def bulk_update_vermuk(
    data: ChannelBulkVermuk,
    cursor=Depends(get_dict_cursor_dep_commit),
):
    """
    Bulk update vermuk status.
    
    Args:
        data: Bulk vermuk data with IDs and status
        cursor: Database cursor with commit
        
    Returns:
        Bulk update result
    """
    try:
        conn = cursor.connection
        
        result = ChannelService.bulk_update_vermuk(
            cursor,
            ids=data.ids,
            vermuk=data.vermuk,
            validate_existence=data.validate_existence,
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Bulk update failed')
            )
        
        conn.commit()
        
        return result
        
    except ChannelsNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except BulkValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except BulkChannelError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except ChannelError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update vermuk: {str(exc)}",
        )


# =====================================================
# BULK UPDATE NOTES
# =====================================================

@router.post(
    "/notes",
    response_model=APIResponse,
    summary="Bulk update notes",
    description="Update notes for multiple channels"
)
async def bulk_update_notes(
    data: ChannelBulkNotes,
    cursor=Depends(get_dict_cursor_dep_commit),
):
    """
    Bulk update notes.
    
    Args:
        data: Bulk notes data with updates dict
        cursor: Database cursor with commit
        
    Returns:
        Bulk update result
    """
    try:
        conn = cursor.connection
        
        result = ChannelService.bulk_update_notes(
            cursor,
            updates=data.updates,
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Bulk update notes failed')
            )
        
        conn.commit()
        
        return result
        
    except InvalidChannelNotesError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except BulkChannelError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except ChannelError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update notes: {str(exc)}",
        )


# =====================================================
# BULK UPSERT
# =====================================================

@router.post(
    "/upsert",
    response_model=APIResponse,
    summary="Bulk upsert channels",
    description="Insert or update multiple channels"
)
async def bulk_upsert(
    channels: List[Dict[str, Any]],
    conflict_column: str = Query("name", description="Column to check for conflicts (name or email)"),
    cursor=Depends(get_dict_cursor_dep_commit),
):
    """
    Bulk upsert channels (insert or update on conflict).
    
    Args:
        channels: List of channel data
        conflict_column: Column to check for conflicts
        cursor: Database cursor with commit
        
    Returns:
        Bulk upsert result
    """
    try:
        conn = cursor.connection
        
        from app.music.repositories.channels.bulk import ChannelBulkRepository
        
        result = ChannelBulkRepository.bulk_upsert(
            cursor,
            channels=channels,
            conflict_column=conflict_column,
        )
        
        conn.commit()
        
        return {
            "success": True,
            "data": result,
            "message": f"Upsert complete: {result['inserted_count']} inserted, {result['updated_count']} updated",
            "status_code": status.HTTP_200_OK,
        }
        
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk upsert: {str(exc)}",
        )


# =====================================================
# BULK IMPORT
# =====================================================

@router.post(
    "/import",
    response_model=APIResponse,
    summary="Bulk import channels",
    description="Import multiple channels at once"
)
async def bulk_import(
    channels: List[Dict[str, Any]],
    skip_duplicates: bool = Query(True, description="Skip duplicate names instead of failing"),
    cursor=Depends(get_dict_cursor_dep_commit),
):
    """
    Bulk import channels.
    
    Args:
        channels: List of channel data
        skip_duplicates: Skip duplicates
        cursor: Database cursor with commit
        
    Returns:
        Bulk import result
    """
    try:
        conn = cursor.connection
        
        from app.music.repositories.channels.bulk import ChannelBulkRepository
        
        result = ChannelBulkRepository.bulk_insert(
            cursor,
            channels=channels,
            skip_duplicates=skip_duplicates,
            return_ids=True,
        )
        
        conn.commit()
        
        return {
            "success": True,
            "data": result,
            "message": f"Import complete: {result['inserted_count']} inserted, "
                      f"{len(result['skipped'])} skipped, {len(result['failed'])} failed",
            "status_code": status.HTTP_200_OK,
        }
        
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk import: {str(exc)}",
        )


# =====================================================
# BULK EXPORT
# =====================================================

@router.post(
    "/export",
    summary="Bulk export channels",
    description="Export specific channels by IDs"
)
async def bulk_export(
    ids: List[int],
    format: str = Query("csv", description="Export format: csv or json"),
    include_stats: bool = Query(False, description="Include statistics"),
    cursor=Depends(get_dict_cursor_dep),
):
    """
    Bulk export channels by IDs.
    
    Args:
        ids: List of channel IDs
        format: Export format (csv or json)
        include_stats: Include statistics
        cursor: Database cursor
        
    Returns:
        Exported file
    """
    try:
        if not ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No channel IDs provided"
            )
        
        # Get channels
        channels = []
        not_found = []
        
        for channel_id in ids:
            try:
                result = ChannelService.get_by_id(
                    cursor,
                    channel_id,
                    include_stats=include_stats,
                    include_activity=False
                )
                if result.get('success'):
                    channels.append(result.get('data'))
                else:
                    not_found.append(channel_id)
            except Exception:
                not_found.append(channel_id)
        
        if not channels:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No channels found for the provided IDs"
            )
        
        # Export as CSV
        if format.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            headers = [
                "ID", "Name", "Email", "Vermuk", "Notes",
                "Created At", "Updated At"
            ]
            if include_stats:
                headers.extend(["Total Artists", "Total Songs", "Uploaded Songs", "Pending Songs"])
            writer.writerow(headers)
            
            # Data rows
            for channel in channels:
                row = [
                    channel.get('id', ''),
                    channel.get('name', ''),
                    channel.get('email', ''),
                    "Yes" if channel.get('vermuk') else "No",
                    channel.get('notes', ''),
                    channel.get('created_at', ''),
                    channel.get('updated_at', ''),
                ]
                if include_stats:
                    row.extend([
                        channel.get('total_artists', 0),
                        channel.get('total_songs', 0),
                        channel.get('uploaded_songs', 0),
                        channel.get('pending_songs', 0),
                    ])
                writer.writerow(row)
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=channels_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
        # Export as JSON
        return {
            "success": True,
            "data": {
                "channels": channels,
                "count": len(channels),
                "not_found": not_found,
                "exported_at": datetime.now().isoformat(),
            },
            "message": f"Exported {len(channels)} channels",
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export channels: {str(exc)}",
        )


# =====================================================
# BULK VALIDATE
# =====================================================

@router.post(
    "/validate",
    summary="Bulk validate channel IDs",
    description="Validate if multiple channel IDs exist"
)
async def bulk_validate(
    ids: List[int],
    cursor=Depends(get_dict_cursor_dep),
):
    """
    Validate multiple channel IDs.
    
    Args:
        ids: List of channel IDs to validate
        cursor: Database cursor
        
    Returns:
        Validation results
    """
    try:
        from app.music.repositories.channels.bulk import ChannelBulkRepository
        
        existing_ids = ChannelBulkRepository.bulk_exists(cursor, ids)
        not_found = [id for id in ids if id not in existing_ids]
        
        return {
            "success": True,
            "data": {
                "valid": len(not_found) == 0,
                "existing_ids": existing_ids,
                "not_found": not_found,
                "total_checked": len(ids),
                "valid_count": len(existing_ids),
                "invalid_count": len(not_found),
            },
            "message": f"Validated {len(ids)} IDs: {len(existing_ids)} valid, {len(not_found)} invalid",
        }
        
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate IDs: {str(exc)}",
        )


# =====================================================
# BULK STATS
# =====================================================

@router.post(
    "/stats",
    summary="Get bulk channel statistics",
    description="Get statistics for multiple channels"
)
async def bulk_stats(
    ids: List[int],
    cursor=Depends(get_dict_cursor_dep),
):
    """
    Get statistics for multiple channels.
    
    Args:
        ids: List of channel IDs
        cursor: Database cursor
        
    Returns:
        Statistics for each channel
    """
    try:
        if not ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No channel IDs provided"
            )
        
        result = {}
        for channel_id in ids:
            try:
                stats = ChannelService.get_channel_stats(cursor, channel_id)
                if stats.get('success'):
                    result[channel_id] = stats.get('data', {})
                else:
                    result[channel_id] = {'error': stats.get('error', 'Channel not found')}
            except Exception as e:
                result[channel_id] = {'error': str(e)}
        
        return {
            "success": True,
            "data": result,
            "message": f"Retrieved statistics for {len(result)} channels",
        }
        
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bulk statistics: {str(exc)}",
        )


# =====================================================
# BULK STATUS UPDATE (Advanced)
# =====================================================

@router.post(
    "/status",
    response_model=APIResponse,
    summary="Bulk update channel status",
    description="Update multiple fields for multiple channels"
)
async def bulk_status_update(
    updates: List[Dict[str, Any]],
    cursor=Depends(get_dict_cursor_dep_commit),
):
    """
    Bulk update multiple fields for channels.
    
    Args:
        updates: List of updates with channel_id and fields
        cursor: Database cursor with commit
        
    Returns:
        Bulk update result
    """
    try:
        conn = cursor.connection
        
        from app.music.repositories.channels.bulk import ChannelBulkRepository
        
        result = ChannelBulkRepository.bulk_update_multiple_fields(
            cursor,
            updates=updates,
        )
        
        conn.commit()
        
        return {
            "success": True,
            "data": result,
            "message": f"Updated {result['updated_count']} channels, {len(result['failed'])} failed",
            "status_code": status.HTTP_200_OK,
        }
        
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update status: {str(exc)}",
        )


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']