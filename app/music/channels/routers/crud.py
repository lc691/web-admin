"""
CRUD Channel Router - Complete Implementation

API routes untuk CRUD operations Channel:
- GET /{id} - Get channel detail
- POST / - Create channel
- PUT /{id} - Update channel
- DELETE /{id} - Delete channel
- PATCH /{id}/notes - Update notes only
- GET /exists/{id} - Check if channel exists
- GET /exists/name/{name} - Check if name exists
- GET /exists/email/{email} - Check if email exists
- POST /bulk - Get multiple channels
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List

from app.core.database import (
    get_dict_cursor_dep,
    get_dict_cursor_dep_commit,
)

from app.music.channels.schemas import (
    ChannelCreate,
    ChannelUpdate,
    ChannelNotesUpdate,
    ChannelResponse,
    APIResponse,
    APIErrorResponse,
)

from app.music.services.channels.exceptions import (
    ChannelError,
    ChannelNotFoundError,
    DuplicateChannelEmailError,
    DuplicateChannelNameError,
    InvalidChannelDataError,
    ChannelPermissionError,
)

from app.music.services.channels.service import ChannelService
from app.music.services.channels.mapper import ChannelMapper

router = APIRouter()


# =====================================================
# DETAIL / GET
# =====================================================

@router.get(
    "/{channel_id}",
    response_model=APIResponse,
    summary="Get channel detail",
    description="Get detailed channel information by ID"
)
async def detail(
    channel_id: int,
    include_stats: bool = Query(True, description="Include statistics"),
    include_activity: bool = Query(False, description="Include activity scoring"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get channel detail by ID.
    
    Args:
        channel_id: Channel ID
        include_stats: Include statistics
        include_activity: Include activity scoring
        db: Database cursor
        
    Returns:
        Channel detail
    """
    try:
        cursor, _ = db
        
        result = ChannelService.get_by_id(
            cursor,
            channel_id,
            include_stats=include_stats,
            include_activity=include_activity
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Channel not found')
            )
        
        return result
        
    except ChannelNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channel: {str(exc)}",
        )


# =====================================================
# CREATE
# =====================================================

@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create channel",
    description="Create a new channel with validation"
)
async def create(
    data: ChannelCreate,
    db=Depends(get_dict_cursor_dep_commit),
):
    """
    Create a new channel.
    
    Args:
        data: Channel creation data
        db: Database cursor with commit
        
    Returns:
        Created channel data
    """
    try:
        cursor, conn = db
        
        result = ChannelService.create(
            cursor,
            name=data.name,
            email=data.email,
            password=data.password,
            vermuk=data.vermuk,
            notes=data.notes,
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to create channel')
            )
        
        # Commit transaction
        conn.commit()
        
        return result

    except (DuplicateChannelNameError, DuplicateChannelEmailError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except InvalidChannelDataError as exc:
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
        # Rollback on error
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create channel: {str(exc)}",
        )


# =====================================================
# UPDATE
# =====================================================

@router.put(
    "/{channel_id}",
    response_model=APIResponse,
    summary="Update channel",
    description="Update an existing channel with validation"
)
async def update(
    channel_id: int,
    data: ChannelUpdate,
    db=Depends(get_dict_cursor_dep_commit),
):
    """
    Update an existing channel.
    
    Args:
        channel_id: Channel ID
        data: Channel update data
        db: Database cursor with commit
        
    Returns:
        Updated channel data
    """
    try:
        cursor, conn = db
        
        # Build update data
        update_data = {
            'channel_id': channel_id,
            'name': data.name if data.name is not None else "",
            'email': data.email,
            'password': data.password,
            'vermuk': data.vermuk if data.vermuk is not None else False,
            'notes': data.notes,
        }
        
        result = ChannelService.update(cursor, **update_data)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to update channel')
            )
        
        conn.commit()
        
        return result

    except ChannelNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except (DuplicateChannelNameError, DuplicateChannelEmailError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except InvalidChannelDataError as exc:
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
            detail=f"Failed to update channel: {str(exc)}",
        )


# =====================================================
# DELETE
# =====================================================

@router.delete(
    "/{channel_id}",
    response_model=APIResponse,
    summary="Delete channel",
    description="Delete a channel (cascade deletes artists and songs)"
)
async def delete(
    channel_id: int,
    soft_delete: bool = Query(False, description="Soft delete (not implemented)"),
    db=Depends(get_dict_cursor_dep_commit),
):
    """
    Delete a channel.
    
    Args:
        channel_id: Channel ID
        soft_delete: Soft delete flag (not implemented)
        db: Database cursor with commit
        
    Returns:
        Deletion result
    """
    try:
        cursor, conn = db
        
        result = ChannelService.delete(cursor, channel_id, soft_delete=soft_delete)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to delete channel')
            )
        
        conn.commit()
        
        return result

    except ChannelNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        )
    except ChannelPermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete channel: {str(exc)}",
        )


# =====================================================
# UPDATE NOTES ONLY
# =====================================================

@router.patch(
    "/{channel_id}/notes",
    response_model=APIResponse,
    summary="Update channel notes",
    description="Update only notes for a channel"
)
async def update_notes(
    channel_id: int,
    data: ChannelNotesUpdate,
    db=Depends(get_dict_cursor_dep_commit),
):
    """
    Update only notes for a channel.
    
    Args:
        channel_id: Channel ID
        data: Notes update data
        db: Database cursor with commit
        
    Returns:
        Updated channel data
    """
    try:
        cursor, conn = db
        
        result = ChannelService.update_notes(
            cursor,
            channel_id=channel_id,
            notes=data.notes,
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to update notes')
            )
        
        conn.commit()
        
        return result

    except ChannelNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except InvalidChannelDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notes: {str(exc)}",
        )


# =====================================================
# PARTIAL UPDATE (PATCH)
# =====================================================

@router.patch(
    "/{channel_id}",
    response_model=APIResponse,
    summary="Partial update channel",
    description="Partially update a channel"
)
async def partial_update(
    channel_id: int,
    data: ChannelUpdate,
    db=Depends(get_dict_cursor_dep_commit),
):
    """
    Partially update a channel (only provided fields).
    
    Args:
        channel_id: Channel ID
        data: Channel update data (partial)
        db: Database cursor with commit
        
    Returns:
        Updated channel data
    """
    try:
        cursor, conn = db
        
        # Get current channel data
        current_result = ChannelService.get_by_id(cursor, channel_id)
        if not current_result.get('success'):
            raise ChannelNotFoundError(channel_id=channel_id)
        
        current = current_result.get('data', {})
        
        # Merge with provided data
        update_data = {
            'channel_id': channel_id,
            'name': data.name if data.name is not None else current.get('name', ''),
            'email': data.email if data.email is not None else current.get('email'),
            'password': data.password if data.password is not None else current.get('password'),
            'vermuk': data.vermuk if data.vermuk is not None else current.get('vermuk', False),
            'notes': data.notes if data.notes is not None else current.get('notes'),
        }
        
        result = ChannelService.update(cursor, **update_data)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to update channel')
            )
        
        conn.commit()
        
        return result

    except ChannelNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except (DuplicateChannelNameError, DuplicateChannelEmailError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except InvalidChannelDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update channel: {str(exc)}",
        )


# =====================================================
# CHECK EXISTS
# =====================================================

@router.get(
    "/exists/{channel_id}",
    summary="Check channel exists",
    description="Check if a channel exists by ID"
)
async def check_exists(
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    """
    Check if a channel exists.
    
    Args:
        channel_id: Channel ID
        db: Database cursor
        
    Returns:
        Existence status
    """
    try:
        cursor, _ = db
        
        from app.music.repositories.channels.repository import ChannelRepository
        
        exists = ChannelRepository.exists(cursor, channel_id)
        
        return {
            "success": True,
            "data": {
                "exists": exists,
                "channel_id": channel_id,
            }
        }
        
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check existence: {str(exc)}",
        )


@router.get(
    "/exists/name/{name}",
    summary="Check channel name exists",
    description="Check if a channel name already exists"
)
async def check_name_exists(
    name: str,
    exclude_id: Optional[int] = Query(None, description="Exclude this ID"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Check if a channel name exists.
    
    Args:
        name: Channel name
        exclude_id: Exclude this ID (for updates)
        db: Database cursor
        
    Returns:
        Existence status
    """
    try:
        cursor, _ = db
        
        from app.music.repositories.channels.repository import ChannelRepository
        
        exists = ChannelRepository.exists_name(cursor, name, exclude_id=exclude_id)
        
        return {
            "success": True,
            "data": {
                "exists": exists,
                "name": name,
                "exclude_id": exclude_id,
            }
        }
        
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check name existence: {str(exc)}",
        )


@router.get(
    "/exists/email/{email}",
    summary="Check channel email exists",
    description="Check if a channel email already exists"
)
async def check_email_exists(
    email: str,
    exclude_id: Optional[int] = Query(None, description="Exclude this ID"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Check if a channel email exists.
    
    Args:
        email: Channel email
        exclude_id: Exclude this ID (for updates)
        db: Database cursor
        
    Returns:
        Existence status
    """
    try:
        cursor, _ = db
        
        from app.music.repositories.channels.repository import ChannelRepository
        
        exists = ChannelRepository.exists_email(cursor, email, exclude_id=exclude_id)
        
        return {
            "success": True,
            "data": {
                "exists": exists,
                "email": email,
                "exclude_id": exclude_id,
            }
        }
        
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check email existence: {str(exc)}",
        )


# =====================================================
# BULK GET (Multiple Channels)
# =====================================================

@router.post(
    "/bulk",
    summary="Get multiple channels",
    description="Get multiple channels by IDs"
)
async def bulk_get(
    channel_ids: List[int],
    include_stats: bool = Query(True, description="Include statistics"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Get multiple channels by IDs.
    
    Args:
        channel_ids: List of channel IDs
        include_stats: Include statistics
        db: Database cursor
        
    Returns:
        List of channels
    """
    try:
        cursor, _ = db
        
        channels = []
        not_found = []
        
        for channel_id in channel_ids:
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
        
        return {
            "success": True,
            "data": {
                "channels": channels,
                "count": len(channels),
                "not_found": not_found,
                "total_requested": len(channel_ids),
            },
            "message": f"Retrieved {len(channels)} channels"
        }
        
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channels: {str(exc)}",
        )


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']