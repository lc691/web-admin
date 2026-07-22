"""
Bulk Channel Router
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_dict_cursor_dep_commit
from app.music.channels.schema import (
    ChannelBulkDelete,
    ChannelBulkVermuk,
)
from app.music.services.channels.exceptions import ChannelError
from app.music.services.channels.service import ChannelService

router = APIRouter()

@router.post("/delete")
async def bulk_delete(
    data: ChannelBulkDelete,
    cursor=Depends(get_dict_cursor_dep_commit),
):
    try:
        deleted = ChannelService.bulk_delete(
            cursor,
            data.ids,
        )

        return {
            "success": True,
            "message": f"{deleted} channel berhasil dihapus.",
            "deleted": deleted,
        }

    except ChannelError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/vermuk")
async def bulk_update_vermuk(
    data: ChannelBulkVermuk,
    cursor=Depends(get_dict_cursor_dep_commit),
):
    try:
        updated = ChannelService.bulk_update_vermuk(
            cursor,
            ids=data.ids,
            vermuk=data.vermuk,
        )

        return {
            "success": True,
            "message": f"{updated} channel berhasil diperbarui.",
            "updated": updated,
        }

    except ChannelError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )