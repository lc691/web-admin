"""
Artist Bulk Router - Complete Implementation

API routes untuk bulk operations Artist:
- DELETE /bulk - Bulk delete artists
- POST /bulk/update-channel - Bulk update channel
- POST /bulk/update-names - Bulk update names
- POST /bulk/insert - Bulk insert artists
- POST /bulk/upsert - Bulk upsert artists
- POST /bulk/validate - Bulk validation
- GET /bulk/summary - Bulk summary
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime

from app.music.artists.schemas import (
    ArtistBulkDelete,
    ArtistBulkUpdateChannel,
    ArtistBulkUpdateNames,
    ArtistBulkInsert,
    ArtistBulkResponse,
    APIResponse,
    APIErrorResponse,
)

from app.music.services.artists.service import ArtistService

from app.music.services.artists.exceptions import (
    ArtistDatabaseError,
    ArtistHasSongsError,
    ArtistNotFoundError,
    ArtistsNotFoundError,
    BulkDeleteError,
    BulkUpdateError,
    BulkInsertError,
    EmptySelectionError,
    InvalidArtistNameError,
    InvalidChannelError,
    ChannelNotFoundError,
)

router = APIRouter()


# =====================================================
# BULK DELETE
# =====================================================

@router.delete(
    "/bulk",
    response_model=APIResponse,
    summary="Bulk delete artists",
    description="Delete multiple artists at once"
)
def bulk_delete(
    data: ArtistBulkDelete,
):
    """
    Bulk Delete Artist.
    
    Args:
        data: Bulk delete data with IDs and force flag
        
    Returns:
        Bulk delete result
    """
    try:
        result = ArtistService.bulk_delete(
            artist_ids=data.ids,
            force=data.force,
        )
        
        return result

    except EmptySelectionError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Empty selection",
                "message": str(exc),
            },
        )
    except ArtistsNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artists not found",
                "message": str(exc),
                "details": exc.details if hasattr(exc, 'details') else None,
            },
        )
    except ArtistHasSongsError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error": "Artists have songs",
                "message": str(exc),
                "details": exc.details if hasattr(exc, 'details') else None,
            },
        )
    except BulkDeleteError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Bulk delete failed",
                "message": str(exc),
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
# BULK UPDATE CHANNEL
# =====================================================

@router.post(
    "/bulk/update-channel",
    response_model=APIResponse,
    summary="Bulk update channel",
    description="Update channel for multiple artists"
)
def bulk_update_channel(
    data: ArtistBulkUpdateChannel,
):
    """
    Bulk update channel for artists.
    
    Args:
        data: Bulk update data with IDs and new channel_id
        
    Returns:
        Bulk update result
    """
    try:
        result = ArtistService.bulk_update_channel(
            artist_ids=data.ids,
            channel_id=data.channel_id,
        )
        
        return result

    except EmptySelectionError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Empty selection",
                "message": str(exc),
            },
        )
    except ArtistsNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artists not found",
                "message": str(exc),
            },
        )
    except (InvalidChannelError, ChannelNotFoundError) as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Invalid channel",
                "message": str(exc),
            },
        )
    except BulkUpdateError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Bulk update failed",
                "message": str(exc),
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
# BULK UPDATE NAMES
# =====================================================

@router.post(
    "/bulk/update-names",
    response_model=APIResponse,
    summary="Bulk update names",
    description="Update names for multiple artists"
)
def bulk_update_names(
    data: ArtistBulkUpdateNames,
):
    """
    Bulk update names for artists.
    
    Args:
        data: Bulk update data with name updates
        
    Returns:
        Bulk update result
    """
    try:
        result = ArtistService.bulk_update_names(
            updates=data.updates,
        )
        
        return result

    except EmptySelectionError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Empty selection",
                "message": str(exc),
            },
        )
    except InvalidArtistNameError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Invalid name",
                "message": str(exc),
            },
        )
    except ArtistsNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artists not found",
                "message": str(exc),
            },
        )
    except BulkUpdateError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Bulk update failed",
                "message": str(exc),
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
# BULK INSERT
# =====================================================

@router.post(
    "/bulk/insert",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk insert artists",
    description="Insert multiple artists at once"
)
def bulk_insert(
    data: ArtistBulkInsert,
):
    """
    Bulk insert artists.
    
    Args:
        data: Bulk insert data with artists list
        
    Returns:
        Bulk insert result
    """
    try:
        result = ArtistService.bulk_insert(
            artists=data.artists,
            skip_duplicates=data.skip_duplicates,
        )
        
        return result

    except EmptySelectionError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Empty selection",
                "message": str(exc),
            },
        )
    except (InvalidArtistNameError, InvalidChannelError) as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Validation error",
                "message": str(exc),
            },
        )
    except BulkInsertError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Bulk insert failed",
                "message": str(exc),
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
# BULK UPSERT
# =====================================================

@router.post(
    "/bulk/upsert",
    response_model=APIResponse,
    summary="Bulk upsert artists",
    description="Insert or update multiple artists"
)
def bulk_upsert(
    artists: List[dict],
    conflict_column: str = Query("name", description="Column to check for conflicts (name or id)"),
):
    """
    Bulk upsert artists (insert or update on conflict).
    
    Args:
        artists: List of artist data
        conflict_column: Column to check for conflicts
        
    Returns:
        Bulk upsert result
    """
    try:
        from app.music.repositories.artists.bulk import ArtistBulkRepository
        from app.core.database import get_dict_cursor_with_commit
        
        with get_dict_cursor_with_commit() as (cursor, conn):
            result = ArtistBulkRepository.bulk_upsert(
                cursor,
                artists=artists,
                conflict_column=conflict_column,
            )
        
        return {
            "success": True,
            "data": result,
            "message": f"Upsert complete: {result['inserted_count']} inserted, {result['updated_count']} updated",
            "status_code": status.HTTP_200_OK,
        }

    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Bulk upsert failed",
                "message": str(exc),
            },
        )


# =====================================================
# BULK VALIDATE
# =====================================================

@router.post(
    "/bulk/validate",
    summary="Bulk validate artists",
    description="Validate multiple artist IDs"
)
def bulk_validate(
    artist_ids: List[int],
):
    """
    Validate multiple artist IDs.
    
    Args:
        artist_ids: List of artist IDs
        
    Returns:
        Validation results
    """
    try:
        from app.music.repositories.artists.bulk import ArtistBulkRepository
        from app.core.database import get_dict_cursor
        
        with get_dict_cursor() as (cursor, conn):
            existing_ids = ArtistBulkRepository.existing_ids(cursor, artist_ids)
            not_found = [id for id in artist_ids if id not in existing_ids]
        
        return {
            "success": True,
            "data": {
                "valid": len(not_found) == 0,
                "existing_ids": existing_ids,
                "not_found": not_found,
                "total_checked": len(artist_ids),
                "valid_count": len(existing_ids),
                "invalid_count": len(not_found),
            },
            "message": f"Validated {len(artist_ids)} IDs: {len(existing_ids)} valid, {len(not_found)} invalid",
        }

    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Validation failed",
                "message": str(exc),
            },
        )


# =====================================================
# BULK SUMMARY
# =====================================================

@router.post(
    "/bulk/summary",
    summary="Bulk artist summary",
    description="Get summary for multiple artists"
)
def bulk_summary(
    artist_ids: List[int],
):
    """
    Get summary for multiple artists.
    
    Args:
        artist_ids: List of artist IDs
        
    Returns:
        Summary data
    """
    try:
        from app.music.repositories.artists.bulk import ArtistBulkRepository
        from app.core.database import get_dict_cursor
        
        with get_dict_cursor() as (cursor, conn):
            summary = ArtistBulkRepository.summary(cursor, artist_ids)
        
        return {
            "success": True,
            "data": summary,
            "artist_ids": artist_ids,
        }

    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Failed to get summary",
                "message": str(exc),
            },
        )


# =====================================================
# BULK EXPORT
# =====================================================

@router.post(
    "/bulk/export",
    summary="Bulk export artists",
    description="Export specific artists by IDs"
)
def bulk_export(
    artist_ids: List[int],
    format: str = Query("json", description="Export format: json or csv"),
    include_stats: bool = Query(True, description="Include statistics"),
):
    """
    Export specific artists by IDs.
    
    Args:
        artist_ids: List of artist IDs
        format: Export format (json or csv)
        include_stats: Include statistics
        
    Returns:
        Exported data
    """
    try:
        from app.music.repositories.artists.bulk import ArtistBulkRepository
        from app.core.database import get_dict_cursor
        
        if not artist_ids:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "Empty selection",
                    "message": "No artist IDs provided",
                },
            )
        
        with get_dict_cursor() as (cursor, conn):
            artists = ArtistBulkRepository.export_artists(
                cursor,
                artist_ids=artist_ids,
                include_songs=include_stats,
            )
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            headers = ["ID", "Name", "Channel ID", "Channel Name", "Song Count", "Created At", "Updated At"]
            if include_stats:
                headers.extend(["Uploaded Songs", "Pending Songs"])
            writer.writerow(headers)
            
            # Data rows
            for artist in artists:
                row = [
                    artist.get('id', ''),
                    artist.get('name', ''),
                    artist.get('channel_id', ''),
                    artist.get('channel_name', ''),
                    artist.get('song_count', 0),
                    artist.get('created_at', ''),
                    artist.get('updated_at', ''),
                ]
                if include_stats:
                    row.extend([
                        artist.get('uploaded_songs', 0),
                        artist.get('pending_songs', 0),
                    ])
                writer.writerow(row)
            
            output.seek(0)
            
            from fastapi.responses import StreamingResponse
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=artists_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        
        return {
            "success": True,
            "data": artists,
            "count": len(artists),
            "total_requested": len(artist_ids),
        }

    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Export failed",
                "message": str(exc),
            },
        )


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']