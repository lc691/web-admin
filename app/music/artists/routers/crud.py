"""
Artist CRUD Router - Complete Implementation

API routes untuk CRUD operations Artist:
- GET /{id} - Get artist detail
- POST / - Create artist
- PUT /{id} - Update artist
- DELETE /{id} - Delete artist
- PATCH /{id}/name - Update name only
- PATCH /{id}/channel - Update channel only
- GET /exists/{id} - Check if artist exists
- GET /exists/name - Check if name exists
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import Optional, List

from app.music.artists.schemas import (
    ArtistCreate,
    ArtistUpdate,
    ArtistResponse,
    ArtistDetail,
    APIResponse,
    APIErrorResponse,
)

from app.music.services.artists.service import ArtistService

from app.music.services.artists.exceptions import (
    ArtistAlreadyExistsError,
    ArtistDatabaseError,
    ArtistDeleteError,
    ArtistHasSongsError,
    ArtistNotFoundError,
    InvalidArtistNameError,
    InvalidChannelError,
    ChannelNotFoundError,
)

router = APIRouter()


# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/{artist_id}",
    response_model=ArtistDetail,
    summary="Get artist detail",
    description="Get detailed artist information by ID"
)
def detail(
    artist_id: int,
    include_songs: bool = Query(True, description="Include song details"),
):
    """
    Get artist detail by ID.
    
    Args:
        artist_id: Artist ID
        include_songs: Include song details
        
    Returns:
        Artist detail
    """
    try:
        return ArtistService.get_detail(
            artist_id,
            include_songs=include_songs,
        )

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
# CREATE
# =====================================================

@router.post(
    "/",
    response_model=ArtistDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create artist",
    description="Create a new artist with validation"
)
def create(
    data: ArtistCreate,
):
    """
    Create a new artist.
    
    Args:
        data: Artist creation data
        
    Returns:
        Created artist data
    """
    try:
        result = ArtistService.create(
            channel_id=data.channel_id,
            name=data.name,
        )
        
        return result

    except (
        ArtistAlreadyExistsError,
        InvalidArtistNameError,
        InvalidChannelError,
    ) as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Validation error",
                "message": str(exc),
                "details": exc.details if hasattr(exc, 'details') else None,
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
# UPDATE
# =====================================================

@router.put(
    "/{artist_id}",
    response_model=ArtistDetail,
    summary="Update artist",
    description="Update an existing artist with validation"
)
def update(
    artist_id: int,
    data: ArtistUpdate,
):
    """
    Update an existing artist.
    
    Args:
        artist_id: Artist ID
        data: Artist update data
        
    Returns:
        Updated artist data
    """
    try:
        # Use existing values if not provided
        if data.channel_id is None or data.name is None:
            # Get current data
            current = ArtistService.get_detail(artist_id)
            channel_id = data.channel_id if data.channel_id is not None else current.get('channel_id')
            name = data.name if data.name is not None else current.get('name')
        else:
            channel_id = data.channel_id
            name = data.name
        
        result = ArtistService.update(
            artist_id=artist_id,
            channel_id=channel_id,
            name=name,
        )
        
        return result

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
    except (
        ArtistAlreadyExistsError,
        InvalidArtistNameError,
        InvalidChannelError,
    ) as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Validation error",
                "message": str(exc),
                "details": exc.details if hasattr(exc, 'details') else None,
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
# DELETE
# =====================================================

@router.delete(
    "/{artist_id}",
    summary="Delete artist",
    description="Delete an artist (check if has songs)"
)
def delete(
    artist_id: int,
    force: bool = Query(False, description="Force delete even if has songs"),
):
    """
    Delete an artist.
    
    Args:
        artist_id: Artist ID
        force: Force delete even if has songs
        
    Returns:
        Deletion result
    """
    try:
        return ArtistService.delete(
            artist_id,
            force=force,
        )

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
    except ArtistHasSongsError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error": "Artist has songs",
                "message": str(exc),
                "artist_id": artist_id,
                "song_count": exc.details.get('song_count', 0) if hasattr(exc, 'details') else 0,
            },
        )
    except ArtistDeleteError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Delete failed",
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
# UPDATE NAME ONLY
# =====================================================

@router.patch(
    "/{artist_id}/name",
    response_model=ArtistDetail,
    summary="Update artist name",
    description="Update only the artist name"
)
def update_name(
    artist_id: int,
    name: str = Query(..., min_length=2, max_length=255, description="New name"),
):
    """
    Update only artist name.
    
    Args:
        artist_id: Artist ID
        name: New name
        
    Returns:
        Updated artist data
    """
    try:
        # Get current data
        current = ArtistService.get_detail(artist_id)
        
        result = ArtistService.update(
            artist_id=artist_id,
            channel_id=current.get('channel_id'),
            name=name,
        )
        
        return result

    except ArtistNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artist not found",
                "message": str(exc),
            },
        )
    except (ArtistAlreadyExistsError, InvalidArtistNameError) as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "Validation error",
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
# UPDATE CHANNEL ONLY
# =====================================================

@router.patch(
    "/{artist_id}/channel",
    response_model=ArtistDetail,
    summary="Update artist channel",
    description="Update only the artist channel"
)
def update_channel(
    artist_id: int,
    channel_id: int = Query(..., ge=1, description="New channel ID"),
):
    """
    Update only artist channel.
    
    Args:
        artist_id: Artist ID
        channel_id: New channel ID
        
    Returns:
        Updated artist data
    """
    try:
        # Get current data
        current = ArtistService.get_detail(artist_id)
        
        result = ArtistService.update(
            artist_id=artist_id,
            channel_id=channel_id,
            name=current.get('name'),
        )
        
        return result

    except ArtistNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "Artist not found",
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
# CHECK EXISTS
# =====================================================

@router.get(
    "/exists/{artist_id}",
    summary="Check artist exists",
    description="Check if an artist exists by ID"
)
def check_exists(
    artist_id: int,
):
    """
    Check if an artist exists.
    
    Args:
        artist_id: Artist ID
        
    Returns:
        Existence status
    """
    try:
        from app.music.repositories.artists.repository import ArtistRepository
        from app.core.database import get_dict_cursor
        
        with get_dict_cursor() as (cursor, conn):
            exists = ArtistRepository.exists(cursor, artist_id)
        
        return {
            "success": True,
            "data": {
                "exists": exists,
                "artist_id": artist_id,
            }
        }

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
# CHECK NAME EXISTS
# =====================================================

@router.get(
    "/exists/name",
    summary="Check artist name exists",
    description="Check if an artist name exists in a channel"
)
def check_name_exists(
    channel_id: int = Query(..., ge=1, description="Channel ID"),
    name: str = Query(..., min_length=2, max_length=255, description="Artist name"),
    exclude_id: Optional[int] = Query(None, ge=1, description="Exclude this ID"),
):
    """
    Check if an artist name exists in a channel.
    
    Args:
        channel_id: Channel ID
        name: Artist name
        exclude_id: Exclude this ID (for updates)
        
    Returns:
        Existence status
    """
    try:
        from app.music.repositories.artists.repository import ArtistRepository
        from app.core.database import get_dict_cursor
        
        with get_dict_cursor() as (cursor, conn):
            exists = ArtistRepository.exists_by_name(
                cursor,
                channel_id=channel_id,
                name=name,
                exclude_id=exclude_id,
            )
        
        return {
            "success": True,
            "data": {
                "exists": exists,
                "channel_id": channel_id,
                "name": name,
                "exclude_id": exclude_id,
            }
        }

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
# BULK GET
# =====================================================

@router.post(
    "/bulk",
    summary="Get multiple artists",
    description="Get multiple artists by IDs"
)
def bulk_get(
    artist_ids: List[int],
    include_stats: bool = Query(True, description="Include statistics"),
):
    """
    Get multiple artists by IDs.
    
    Args:
        artist_ids: List of artist IDs
        include_stats: Include statistics
        
    Returns:
        List of artists
    """
    try:
        artists = []
        not_found = []
        
        for artist_id in artist_ids:
            try:
                artist = ArtistService.get_detail(artist_id)
                artists.append(artist)
            except ArtistNotFoundError:
                not_found.append(artist_id)
        
        return {
            "success": True,
            "data": {
                "artists": artists,
                "count": len(artists),
                "not_found": not_found,
                "total_requested": len(artist_ids),
            },
            "message": f"Retrieved {len(artists)} artists",
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