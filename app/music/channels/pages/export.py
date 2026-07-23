"""
Channel Export Page
"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.templates import templates

router = APIRouter()


# =====================================================
# EXPORT
# =====================================================

@router.get(
    "/channels/export",
    response_class=HTMLResponse,
)
async def export(
    request: Request,
    format: str = Query("xlsx", pattern="^(xlsx|csv|json)$"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman export channel.
    """

    try:

        cursor, _ = db

        context = ChannelPresenter.export(
            cursor,
            format,
        )

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
                "message": "Gagal memuat halaman export channel",
            },
            status_code=500,
        )


__all__ = ["router"]