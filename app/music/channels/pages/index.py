"""
Channel Index Page
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.templates import templates

router = APIRouter()


# =====================================================
# INDEX
# =====================================================

@router.get(
    "/channels",
    response_class=HTMLResponse,
)
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

        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "message": "Gagal memuat daftar channel",
            },
            status_code=500,
        )


__all__ = ["router"]