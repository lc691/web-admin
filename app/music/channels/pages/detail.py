"""
Channel Detail Page
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.music.services.channels.exceptions import ChannelNotFoundError
from app.templates import templates

router = APIRouter()


# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/channels/{channel_id}",
    response_class=HTMLResponse,
)
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

        context = ChannelPresenter.detail(
            cursor,
            channel_id,
        )

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
                "message": f"Gagal memuat detail channel ID: {channel_id}",
            },
            status_code=500,
        )


__all__ = ["router"]