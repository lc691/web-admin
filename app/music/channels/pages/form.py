"""
Channel Form Pages
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.music.services.channels.exceptions import ChannelNotFoundError
from app.templates import templates

router = APIRouter()


# =====================================================
# CREATE
# =====================================================

@router.get(
    "/channels/create",
    response_class=HTMLResponse,
)
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
                "message": "Gagal memuat halaman tambah channel",
            },
            status_code=500,
        )


# =====================================================
# EDIT
# =====================================================

@router.get(
    "/channels/{channel_id}/edit",
    response_class=HTMLResponse,
)
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

        context = ChannelPresenter.edit(
            cursor,
            channel_id,
        )

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
                "message": f"Gagal memuat halaman edit channel ID: {channel_id}",
            },
            status_code=500,
        )


__all__ = ["router"]