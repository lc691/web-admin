"""
Channel Compare Page
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.templates import templates

router = APIRouter()


# =====================================================
# COMPARE
# =====================================================

@router.get(
    "/channels/compare",
    response_class=HTMLResponse,
)
async def compare(
    request: Request,
    ids: str = "",
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman perbandingan channel.
    """

    try:

        channel_ids = [
            int(channel_id.strip())
            for channel_id in ids.split(",")
            if channel_id.strip()
        ]

        cursor, _ = db

        context = ChannelPresenter.compare(
            cursor,
            channel_ids,
        )

        context["request"] = request

        return templates.TemplateResponse(
            "music/channels/compare.html",
            context,
        )

    except ValueError:

        return templates.TemplateResponse(
            "errors/400.html",
            {
                "request": request,
                "message": "Parameter ids harus berupa daftar ID numerik yang dipisahkan koma.",
            },
            status_code=400,
        )

    except Exception as e:

        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat halaman perbandingan channel",
            },
            status_code=500,
        )


__all__ = ["router"]