"""
Channel Data Router
"""

from fastapi import APIRouter, Depends, Request

from app.core.database import get_dict_cursor_dep
from app.core.datatable import DataTable
from app.music.services.channels.service import ChannelService

router = APIRouter()


@router.get("/data")
async def data(
    request: Request,
    db=Depends(get_dict_cursor_dep),
):

    cursor, _ = db

    dt = DataTable(request)

    rows = ChannelService.datatable(
        cursor,
        dt,
    )

    filtered = ChannelService.count_filtered(
        cursor,
        dt,
    )

    statistics = ChannelService.statistics(
        cursor,
    )

    return dt.response(
        data=rows,
        total=statistics["total_channels"],
        filtered=filtered,
    )