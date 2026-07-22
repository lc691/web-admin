"""
Channel Statistics Router
"""

from fastapi import APIRouter, Depends

from app.core.database import get_dict_cursor_dep
from app.music.services.channels.service import ChannelService

router = APIRouter()


@router.get("/statistics")
async def statistics(
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    return ChannelService.statistics(cursor)