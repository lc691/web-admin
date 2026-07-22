"""
Channel Pages
"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from typing import Optional

from app.core.database import get_dict_cursor_dep
from app.templates import templates
from app.music.channels.presenter import ChannelPresenter
from app.music.services.channels.service import ChannelService

router = APIRouter(
    tags=["Channels Pages"],
)


# =====================================================
# LIST
# =====================================================

@router.get(
    "/channels",
    response_class=HTMLResponse,
)
def list_channels(
    request: Request,
    keyword: Optional[str] = Query(None, description="Search keyword"),
    year: Optional[int] = Query(None, description="Filter by year"),
    has_youtube: Optional[str] = Query(None, description="Filter by YouTube presence: 'true' or 'false'"),
    has_artists: Optional[str] = Query(None, description="Filter by artists: 'true' or 'false'"),
    has_songs: Optional[str] = Query(None, description="Filter by songs: 'true' or 'false'"),
    # Remove page and per_page parameters or set default to show all
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    # Convert string parameters to boolean/None
    def parse_bool_param(value: Optional[str]) -> Optional[bool]:
        if value is None or value == "":
            return None
        return value.lower() == "true"

    service = ChannelService(cursor)

    # Get all channels without pagination limit
    channels = service.filter(
        keyword=keyword,
        year=year,
        has_youtube=parse_bool_param(has_youtube),
        has_artists=parse_bool_param(has_artists),
        has_songs=parse_bool_param(has_songs),
        # Remove limit and offset to show all
    )

    # Get total count
    total_count = service.count_filtered(
        keyword=keyword,
        year=year,
        has_youtube=parse_bool_param(has_youtube),
        has_artists=parse_bool_param(has_artists),
        has_songs=parse_bool_param(has_songs),
    )

    context = ChannelPresenter.list(
        channels=channels,
        years=service.years(),
        keyword=keyword,
        year=year,
        has_youtube=parse_bool_param(has_youtube),
        has_artists=parse_bool_param(has_artists),
        has_songs=parse_bool_param(has_songs),
        total=total_count,
        # Remove pagination parameters
    )

    return templates.TemplateResponse(
        request,
        "channels/index.html",
        {
            "request": request,
            **context,
        },
    )


# =====================================================
# CREATE PAGE
# =====================================================

@router.get(
    "/channels/new",
    response_class=HTMLResponse,
)
def create_channel_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "channels/form.html",
        ChannelPresenter.form(),
    )


# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/channels/{channel_id}",
    response_class=HTMLResponse,
)
def channel_detail(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    service = ChannelService(cursor)

    detail = service.get_detail(channel_id)

    context = ChannelPresenter.detail(**detail)

    return templates.TemplateResponse(
        request,
        "channels/details.html",
        context,
    )


# =====================================================
# EDIT PAGE
# =====================================================

@router.get(
    "/channels/{channel_id}/edit",
    response_class=HTMLResponse,
)
def edit_channel_page(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    service = ChannelService(cursor)

    channel = service.get(channel_id)

    context = ChannelPresenter.form(
        channel=channel,
    )

    return templates.TemplateResponse(
        request,
        "channels/form.html",
        context,
    )