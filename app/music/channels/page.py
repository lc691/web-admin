"""
Channel Page Router
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core.database import get_dict_cursor_dep
from app.music.channels.presenter import ChannelPresenter
from app.templates import templates

router = APIRouter(
    tags=["Channels Pages"],
)


@router.get("/channels", response_class=HTMLResponse)
async def index(request: Request):

    context = ChannelPresenter.index()

    context["request"] = request

    return templates.TemplateResponse(
        "music/channels/index.html",
        context,
    )


@router.get(
    "/channels/create",
    response_class=HTMLResponse,
)
async def create(
    request: Request,
):

    context = ChannelPresenter.create()

    context["request"] = request

    return templates.TemplateResponse(
        "music/channels/form.html",
        context,
    )


@router.get(
    "/channels/{channel_id}",
    response_class=HTMLResponse,
)
async def detail(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):

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


@router.get(
    "/channels/{channel_id}/edit",
    response_class=HTMLResponse,
)
async def edit(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):

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