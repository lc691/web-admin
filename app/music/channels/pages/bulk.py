"""
Channel Bulk Page
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.music.channels.presenter import ChannelPresenter
from app.templates import templates

router = APIRouter()


# =====================================================
# BULK OPERATIONS
# =====================================================

@router.get(
    "/channels/bulk",
    response_class=HTMLResponse,
)
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
                "message": "Gagal memuat halaman bulk operations",
            },
            status_code=500,
        )


__all__ = ["router"]