"""
Channel Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Form, Query, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.core.database import (
    get_dict_cursor_dep,
    get_dict_cursor_dep_commit,
)
from app.music.channels.presenter import ChannelPresenter
from app.music.services.channels.bulk import ChannelBulkService
from app.music.services.channels.create import ChannelCreateService
from app.music.services.channels.delete import ChannelDeleteService
from app.music.services.channels.service import ChannelService
from app.music.services.channels.update import ChannelUpdateService

router = APIRouter(
    prefix="/channels",
    tags=["Channels"],
)


# =====================================================
# CREATE
# =====================================================

@router.post("/new")
def create_channel(
    name: str = Form(...),
    youtube_url: Optional[str] = Form(None),
    db=Depends(get_dict_cursor_dep_commit),
):
    cursor, conn = db

    channel_id = ChannelCreateService(cursor).execute(
        name=name,
        youtube_url=youtube_url,
    )
    conn.commit()

    return RedirectResponse(
        url=f"/channels/{channel_id}",
        status_code=HTTP_302_FOUND,
    )


# =====================================================
# UPDATE
# =====================================================

@router.post("/{channel_id}/edit")
def update_channel(
    channel_id: int,
    name: str = Form(...),
    youtube_url: Optional[str] = Form(None),
    db=Depends(get_dict_cursor_dep_commit),
):
    cursor, conn = db

    ChannelUpdateService(cursor).execute(
        channel_id=channel_id,
        name=name,
        youtube_url=youtube_url,
    )
    conn.commit()

    return RedirectResponse(
        url=f"/channels/{channel_id}",
        status_code=HTTP_302_FOUND,
    )


# =====================================================
# DELETE
# =====================================================

@router.post("/{channel_id}/delete")
def delete_channel(
    channel_id: int,
    db=Depends(get_dict_cursor_dep_commit),
):
    cursor, conn = db

    ChannelDeleteService(cursor, conn).execute(channel_id)

    return RedirectResponse(
        url="/channels",
        status_code=HTTP_302_FOUND,
    )


# =====================================================
# BULK DELETE
# =====================================================

@router.post("/bulk-delete")
def bulk_delete(
    channel_ids: str = Form(...),  # Comma-separated IDs
    db=Depends(get_dict_cursor_dep_commit),
):
    cursor, conn = db
    
    # Parse IDs from comma-separated string
    try:
        ids = [int(id.strip()) for id in channel_ids.split(",") if id.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Format ID channel tidak valid.",
        )

    result = ChannelBulkService(cursor, conn).delete(ids)

    return RedirectResponse(
        url="/channels",
        status_code=HTTP_302_FOUND,
    )


# =====================================================
# SEARCH API
# =====================================================

@router.get("/api/search")
def search_channel(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    data = ChannelService(cursor).search(q, limit)

    return JSONResponse(
        content=ChannelPresenter.api(
            data=data,
            total=len(data),
        )
    )


@router.get("/api/autocomplete")
def autocomplete_channel(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    data = ChannelService(cursor).autocomplete(q, limit)

    return JSONResponse(
        content=ChannelPresenter.api(
            data=data,
            total=len(data),
        )
    )


# =====================================================
# STATISTICS API
# =====================================================

@router.get("/api/stats")
def channel_statistics(
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    overview = ChannelService(cursor).overview()

    return JSONResponse(
        content=ChannelPresenter.api(
            data=overview,
        )
    )


@router.get("/api/top")
def top_channels(
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    data = ChannelService(cursor).top_channels(limit)

    return JSONResponse(
        content=ChannelPresenter.api(
            data=data,
            total=len(data),
        )
    )