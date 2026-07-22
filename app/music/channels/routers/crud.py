"""
CRUD Channel Router
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import (
    get_dict_cursor_dep,
    get_dict_cursor_dep_commit,
)

from app.music.channels.schema import (
    ChannelCreate,
    ChannelUpdate,
)

from app.music.services.channels.exceptions import (
    ChannelError,
    ChannelNotFoundError,
    DuplicateChannelEmailError,
    DuplicateChannelNameError,
)

from app.music.services.channels.service import ChannelService

router = APIRouter()


@router.get("/{channel_id}")
async def detail(
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):

    cursor, _ = db

    try:

        return ChannelService.detail(
            cursor,
            channel_id,
        )

    except ChannelNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/create")
async def create(
    data: ChannelCreate,
    db=Depends(get_dict_cursor_dep_commit),
):

    cursor, _ = db

    try:

        channel_id = ChannelService.create(
            cursor,
            name=data.name,
            email=data.email,
            password=data.password,
            vermuk=data.vermuk,
            notes=data.notes,
        )

        return {
            "success": True,
            "message": "Channel berhasil dibuat.",
            "id": channel_id,
        }

    except (
        DuplicateChannelNameError,
        DuplicateChannelEmailError,
    ) as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except ChannelError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/{channel_id}/edit")
async def update(
    channel_id: int,
    data: ChannelUpdate,
    db=Depends(get_dict_cursor_dep_commit),
):

    cursor, _ = db

    try:

        ChannelService.update(
            cursor,
            channel_id=channel_id,
            name=data.name,
            email=data.email,
            password=data.password,
            vermuk=data.vermuk,
            notes=data.notes,
        )

        return {
            "success": True,
            "message": "Channel berhasil diperbarui.",
        }

    except ChannelNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except (
        DuplicateChannelNameError,
        DuplicateChannelEmailError,
    ) as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except ChannelError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/{channel_id}/delete")
async def delete(
    channel_id: int,
    db=Depends(get_dict_cursor_dep_commit),
):

    cursor, _ = db

    try:

        ChannelService.delete(
            cursor,
            channel_id,
        )

        return {
            "success": True,
            "message": "Channel berhasil dihapus.",
        }

    except ChannelNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )