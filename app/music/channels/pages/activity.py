"""
Channel Activity Page
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.music.services.channels.exceptions import ChannelNotFoundError
from app.templates import templates

router = APIRouter()


# =====================================================
# CHANNEL ACTIVITY
# =====================================================

@router.get(
    "/channels/{channel_id}/activity",
    response_class=HTMLResponse,
)
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

        context = ChannelPresenter.activity(
            cursor,
            channel_id,
        )

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
                "message": f"Gagal memuat halaman activity channel ID: {channel_id}",
            },
            status_code=500,
        )


__all__ = ["router"]