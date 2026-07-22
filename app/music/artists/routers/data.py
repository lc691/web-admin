"""
Artist Data Router
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.music.artists.schema import (
    ArtistDataTable,
    ArtistResponse,
)
from app.music.services.artists.exceptions import (
    ArtistDatabaseError,
    ArtistNotFoundError,
)
from app.music.services.artists.service import ArtistService

router = APIRouter()


# =====================================================
# DATATABLE
# =====================================================

@router.get(
    "/data",
    response_model=ArtistDataTable,
)
def datatable(
    draw: int = Query(0),
    start: int = Query(0, ge=0),
    length: int = Query(10, ge=1),
    search: str = Query(""),
    channel_id: int | None = Query(None),
    order_column: int = Query(1),
    order_dir: str = Query("desc"),
):
    """
    DataTables Artist.
    """

    try:
        return ArtistService.datatable(
            draw=draw,
            start=start,
            length=length,
            search=search,
            channel_id=channel_id,
            order_column=order_column,
            order_dir=order_dir,
        )

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )


# =====================================================
# SEARCH
# =====================================================

@router.get(
    "/search",
    response_model=list[ArtistResponse],
)
def search(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Search Artist.
    """

    try:
        return ArtistService.search(
            keyword,
            limit,
        )

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )


# =====================================================
# CHANNELS
# =====================================================

@router.get(
    "/channels",
)
def channels():
    """
    Dropdown Channel.
    """

    try:
        return ArtistService.get_channels()

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )