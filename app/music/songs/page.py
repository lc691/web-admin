"""
Songs Page
==========

HTML routes untuk feature Songs.

Page hanya bertanggung jawab merender template.
Seluruh data disiapkan oleh Presenter.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.templates import templates

from .presenter import (
    build_dashboard_context,
    build_detail_context,
    build_form_context,
    build_index_context,
)

router = APIRouter(
    tags=[
        "Songs Pages",
    ],
)

# ==========================================================
# INDEX
# ==========================================================


@router.get(
    "/songs",
    response_class=HTMLResponse,
)
async def index(
    request: Request,
):
    """
    Songs page.
    """

    context = build_index_context()

    return templates.TemplateResponse(
        request=request,
        name="songs/index.html",
        context={
            "request": request,
            **context,
        },
    )


# ==========================================================
# CREATE
# ==========================================================


@router.get(
    "/songs/create",
    response_class=HTMLResponse,
)
async def create(
    request: Request,
):
    """
    Create song form.
    """

    context = build_form_context()

    return templates.TemplateResponse(
        request=request,
        name="songs/form.html",
        context={
            "request": request,
            **context,
        },
    )


# ==========================================================
# EDIT
# ==========================================================


@router.get(
    "/songs/{song_id}/edit",
    response_class=HTMLResponse,
)
async def edit(
    request: Request,
    song_id: int,
):
    """
    Edit song form.
    """

    from app.music.repositories.songs.songs import get_song

    song = get_song(song_id)

    context = build_form_context()
    context["song"] = song

    return templates.TemplateResponse(
        request=request,
        name="songs/form.html",
        context={
            "request": request,
            **context,
        },
    )

# ==========================================================
# YOUTUBE GENERATOR
# ==========================================================

@router.get(
    "/songs/youtube-generator",
    response_class=HTMLResponse,
)
def youtube_generator_page(
    request: Request,
):
    return templates.TemplateResponse(
        "songs/generate.html",
        {
            "request": request,
        },
    )

# ==========================================================
# DETAIL
# ==========================================================


@router.get(
    "/songs/{song_id}",
    response_class=HTMLResponse,
)
async def detail(
    request: Request,
    song_id: int,
):
    """
    Song detail page.
    """

    from app.music.repositories.songs.songs import get_song

    song = get_song(song_id)

    context = build_detail_context(song)

    return templates.TemplateResponse(
        request=request,
        name="songs/detail.html",
        context={
            "request": request,
            **context,
        },
    )


# ==========================================================
# DASHBOARD
# ==========================================================


@router.get(
    "/songs/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
):
    """
    Songs dashboard.
    """

    context = build_dashboard_context()

    return templates.TemplateResponse(
        request=request,
        name="songs/components/stats.html",
        context={
            "request": request,
            **context,
        },
    )


