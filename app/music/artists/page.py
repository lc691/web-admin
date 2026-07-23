"""
Artist Page Router
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.core.database import get_dict_cursor_dep

from app.templates import templates
from app.music.artists.presenter import ArtistPresenter

router = APIRouter(
    tags=["Arists Pages"],
)

# =====================================================
# LIST
# =====================================================
@router.get(
    "/channels/{channel_id}/artists",
    response_class=HTMLResponse,
)
def channel_artists(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    context = ArtistPresenter.channel(
        cursor,
        channel_id,
    )

    context["request"] = request

    return templates.TemplateResponse(
        "music/artists/index.html",
        context,
    )

@router.get(
    "/artists",
    response_class=HTMLResponse,
)
def index(
    request: Request,
):
    """
    Halaman Artist.
    """

    context = ArtistPresenter.list()

    context["request"] = request

    return templates.TemplateResponse(
        "music/artists/index.html",
        context,
    )


# =====================================================
# CREATE
# =====================================================

@router.get(
    "/artists/create",
    response_class=HTMLResponse,
)
def create(
    request: Request,
):
    """
    Form tambah artist.
    """

    context = ArtistPresenter.create()

    context["request"] = request

    return templates.TemplateResponse(
        "music/artists/create.html",
        context,
    )


# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/artists/{artist_id}",
    response_class=HTMLResponse,
)
def detail(
    artist_id: int,
    request: Request,
):
    """
    Detail artist.
    """

    context = ArtistPresenter.detail(
        artist_id,
    )

    context["request"] = request

    return templates.TemplateResponse(
        "music/artists/detail.html",
        context,
    )


# =====================================================
# EDIT
# =====================================================

@router.get(
    "/artists/{artist_id}/edit",
    response_class=HTMLResponse,
)
def edit(
    artist_id: int,
    request: Request,
):
    """
    Form edit artist.
    """

    context = ArtistPresenter.edit(
        artist_id,
    )

    context["request"] = request

    return templates.TemplateResponse(
        "music/artists/edit.html",
        context,
    )