"""
Channel Statistics Page
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.templates import templates

router = APIRouter()


@router.get(
    "/channels/statistics",
    response_class=HTMLResponse,
)
async def statistics(
    request: Request,
    detailed: bool = False,
    period: str = "monthly",
    db=Depends(get_dict_cursor_dep),
):
    try:

        cursor, _ = db

        context = ChannelPresenter.statistics(
            cursor,
            detailed,
            period,
        )

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
                "message": "Gagal memuat halaman statistik",
            },
            status_code=500,
        )


__all__ = ["router"]