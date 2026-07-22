"""
Songs Page
==========

HTML routes untuk feature Songs.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.music.services.songs import service
from app.templates import templates

from .presenter import (
    build_dashboard_context,
    build_detail_context,
    build_form_context,
    build_index_context,
)

router = APIRouter(tags=["Songs Pages"])


# ==========================================================
# INDEX
# ==========================================================

@router.get(
    "/songs",
    response_class=HTMLResponse,
)
async def index(request: Request):
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
# YOUTUBE GENERATOR
# ==========================================================

@router.get(
    "/songs/youtube-generator",
    response_class=HTMLResponse,
)
async def youtube_generator(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="songs/generate.html",
        context={
            "request": request,
        },
    )


# ==========================================================
# CREATE
# ==========================================================

@router.get(
    "/songs/new",
    response_class=HTMLResponse,
)
async def create(request: Request):
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
    song = service.get_song(song_id)

    context = build_detail_context(song)

    return templates.TemplateResponse(
        request=request,
        name="songs/form.html",
        context={
            "request": request,
            **context,
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
    song = service.get_song(song_id)

    context = build_form_context(song)

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
    context = build_dashboard_context()

    return templates.TemplateResponse(
        request=request,
        name="songs/dashboard.html",
        context={
            "request": request,
            **context,
        },
    )