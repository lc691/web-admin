"""
Channel Page Router - Complete Implementation

Routes untuk halaman Channel (Jinja2 templates):
- Index / List
- Create
- Edit
- Detail
- Statistics
- Bulk Operations
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.music.channels.artists_presenter import ChannelArtistsPresenter
from app.music.services.channels.exceptions import (
    ChannelNotFoundError,
    ChannelError,
)
from app.templates import templates

router = APIRouter(
    tags=["Channels Pages"],
)


# =====================================================
# INDEX / LIST
# =====================================================

@router.get("/channels", response_class=HTMLResponse)
async def index(
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman daftar channel.
    """
    try:
        cursor, _ = db
        context = ChannelPresenter.index(cursor)
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/index.html",
            context,
        )
    except Exception as e:
        # Handle error
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat daftar channel"
            },
            status_code=500,
        )

# =====================================================
# STATISTICS
# =====================================================

@router.get("/channels/statistics", response_class=HTMLResponse)
async def statistics(
    request: Request,
    detailed: bool = False,
    period: str = "monthly",
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman statistik channel.
    """
    try:
        cursor, _ = db
        context = ChannelPresenter.statistics(cursor, detailed, period)
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/statistics.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat halaman statistik"
            },
            status_code=500,
        )


# =====================================================
# BULK OPERATIONS
# =====================================================

@router.get("/channels/bulk", response_class=HTMLResponse)
async def bulk(
    request: Request,
):
    """
    Halaman bulk operations channel.
    """
    try:
        context = ChannelPresenter.bulk()
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/bulk.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat halaman bulk operations"
            },
            status_code=500,
        )

# =====================================================
# COMPARE CHANNELS
# =====================================================

@router.get("/channels/compare", response_class=HTMLResponse)
async def compare(
    request: Request,
    ids: str = "",
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman perbandingan channel.
    """
    try:
        channel_ids = [int(id.strip()) for id in ids.split(",") if id.strip()]
        
        cursor, _ = db
        context = ChannelPresenter.compare(cursor, channel_ids)
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/compare.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat halaman perbandingan channel"
            },
            status_code=500,
        )

# =====================================================
# EXPORT
# =====================================================

@router.get("/channels/export", response_class=HTMLResponse)
async def export(
    request: Request,
    format: str = "csv",
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman export channel.
    """
    try:
        cursor, _ = db
        context = ChannelPresenter.export(cursor, format)
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/export.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat halaman export"
            },
            status_code=500,
        )

# =====================================================
# CREATE
# =====================================================

@router.get("/channels/create", response_class=HTMLResponse)
async def create(
    request: Request,
):
    """
    Halaman tambah channel.
    """
    try:
        context = ChannelPresenter.create()
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/form.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat halaman tambah channel"
            },
            status_code=500,
        )


# =====================================================
# DETAIL
# =====================================================

@router.get("/channels/{channel_id}", response_class=HTMLResponse)
async def detail(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman detail channel.
    """
    try:
        cursor, _ = db
        context = ChannelPresenter.detail(cursor, channel_id)
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/detail.html",
            context,
        )
    except ChannelNotFoundError as e:
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "message": str(e),
                "resource": "Channel",
                "resource_id": channel_id,
            },
            status_code=404,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": f"Gagal memuat detail channel ID: {channel_id}"
            },
            status_code=500,
        )


# =====================================================
# EDIT
# =====================================================

@router.get("/channels/{channel_id}/edit", response_class=HTMLResponse)
async def edit(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman edit channel.
    """
    try:
        cursor, _ = db
        context = ChannelPresenter.edit(cursor, channel_id)
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/form.html",
            context,
        )
    except ChannelNotFoundError as e:
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "message": str(e),
                "resource": "Channel",
                "resource_id": channel_id,
            },
            status_code=404,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": f"Gagal memuat halaman edit channel ID: {channel_id}"
            },
            status_code=500,
        )

@router.get(
    "/channels/{channel_id}/artists",
    response_class=HTMLResponse,
)
async def artists(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    context = ChannelArtistsPresenter.page(
        cursor,
        channel_id,
    )

    context["request"] = request

    return templates.TemplateResponse(
        "music/artists/index.html",
        context,
    )
# =====================================================
# CHANNEL ACTIVITY
# =====================================================

@router.get("/channels/{channel_id}/activity", response_class=HTMLResponse)
async def activity(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman activity channel.
    """
    try:
        cursor, _ = db
        context = ChannelPresenter.activity(cursor, channel_id)
        context["request"] = request
        
        return templates.TemplateResponse(
            "music/channels/activity.html",
            context,
        )
    except ChannelNotFoundError as e:
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "message": str(e),
                "resource": "Channel",
                "resource_id": channel_id,
            },
            status_code=404,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": f"Gagal memuat halaman activity channel ID: {channel_id}"
            },
            status_code=500,
        )

# =====================================================
# REDIRECTS
# =====================================================

@router.get("/channels/{channel_id}/view")
async def redirect_to_detail(
    channel_id: int,
):
    """
    Redirect to detail page.
    """
    return RedirectResponse(
        url=f"/channels/{channel_id}",
        status_code=HTTP_302_FOUND
    )


@router.get("/channels/{channel_id}/edit")
async def redirect_to_edit(
    channel_id: int,
):
    """
    Redirect to edit page.
    """
    return RedirectResponse(
        url=f"/channels/{channel_id}/edit",
        status_code=HTTP_302_FOUND
    )


# =====================================================
# ERROR HANDLERS
# =====================================================

@router.get("/channels/error", response_class=HTMLResponse)
async def error_page(
    request: Request,
    message: str = "Terjadi kesalahan",
    status_code: int = 400,
):
    """
    Halaman error generic.
    """
    return templates.TemplateResponse(
        "errors/generic.html",
        {
            "request": request,
            "message": message,
            "status_code": status_code,
        },
        status_code=status_code,
    )


# =====================================================
# NOT FOUND
# =====================================================

@router.get("/channels/not-found", response_class=HTMLResponse)
async def not_found_page(
    request: Request,
    message: str = "Channel tidak ditemukan",
):
    """
    Halaman not found.
    """
    return templates.TemplateResponse(
        "errors/404.html",
        {
            "request": request,
            "message": message,
            "resource": "Channel",
        },
        status_code=404,
    )


# =====================================================
# PERMISSION DENIED
# =====================================================

@router.get("/channels/forbidden", response_class=HTMLResponse)
async def forbidden_page(
    request: Request,
    message: str = "Anda tidak memiliki akses ke halaman ini",
):
    """
    Halaman forbidden.
    """
    return templates.TemplateResponse(
        "errors/403.html",
        {
            "request": request,
            "message": message,
        },
        status_code=403,
    )


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']