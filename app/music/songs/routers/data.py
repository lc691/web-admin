"""
Songs Data Router
=================

Server-side DataTables endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Query

from app.music.services.songs import service
from app.music.services.songs.search import build_response

router = APIRouter(
    prefix="/songs",
    tags=["Songs Data"],
)


# ==========================================================
# DATATABLES
# ==========================================================


@router.get("/data")
def data(
    draw: int = Query(1),
    start: int = Query(0, ge=0),
    length: int = Query(25, ge=1, le=100),
    keyword: str | None = Query(None),
    channel_id: int | None = Query(None),
    artist_id: int | None = Query(None),
    status: str | None = Query(None),
    order_by: str = Query("s.id"),
    descending: bool = Query(True),
):
    """
    DataTables endpoint.
    """

    filters = service.get_filters(
        keyword=keyword,
        channel_id=channel_id,
        artist_id=artist_id,
        status=status,
    )

    return build_response(
        draw=draw,
        filters=filters,
        start=start,
        length=length,
        order_by=order_by,
        descending=descending,
    )