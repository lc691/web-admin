"""
Artist Page Router - Complete Implementation

Routes untuk halaman Artist (Jinja2 templates):
- Index / List
- Create
- Edit
- Detail
- Channel Artists
- Statistics
- Bulk Operations
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.database import get_dict_cursor_dep
from app.templates import templates
from app.music.artists.presenter import ArtistPresenter
from app.music.services.artists.exceptions import (
    ArtistNotFoundError,
    ChannelNotFoundError,
    ArtistDatabaseError,
)

router = APIRouter(
    tags=["Artists Pages"],
)


# =====================================================
# INDEX / LIST
# =====================================================

@router.get(
    "/artists",
    response_class=HTMLResponse,
    summary="Artists list page",
    description="Halaman daftar artist"
)
def index(
    request: Request,
):
    """
    Halaman Artist.
    """
    try:
        context = ArtistPresenter.list()
        context["request"] = request

        return templates.TemplateResponse(
            "music/artists/index.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "message": "Gagal memuat daftar artist",
                "error": str(e),
            },
            status_code=500,
        )

# =====================================================
# STATISTICS
# =====================================================

@router.get(
    "/artists/statistics",
    response_class=HTMLResponse,
    summary="Artist statistics page",
    description="Halaman statistik artist"
)
def statistics(
    request: Request,
    channel_id: int = None,
    detailed: bool = False,
):
    """
    Halaman statistik artist.
    """
    try:
        context = ArtistPresenter.statistics(
            channel_id=channel_id,
            detailed=detailed,
        )
        context["request"] = request

        return templates.TemplateResponse(
            "music/artists/statistics.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "message": "Gagal memuat halaman statistik",
                "error": str(e),
            },
            status_code=500,
        )


# =====================================================
# BULK OPERATIONS
# =====================================================

@router.get(
    "/artists/bulk",
    response_class=HTMLResponse,
    summary="Bulk operations page",
    description="Halaman bulk operations artist"
)
def bulk_operations(
    request: Request,
):
    """
    Halaman bulk operations artist.
    """
    try:
        context = ArtistPresenter.bulk_operations()
        context["request"] = request

        return templates.TemplateResponse(
            "music/artists/bulk.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "message": "Gagal memuat halaman bulk operations",
                "error": str(e),
            },
            status_code=500,
        )


# =====================================================
# CHANNEL ARTISTS
# =====================================================

@router.get(
    "/channels/{channel_id}/artists",
    response_class=HTMLResponse,
    summary="Channel artists page",
    description="Halaman artist berdasarkan channel"
)
def channel_artists(
    request: Request,
    channel_id: int,
    db=Depends(get_dict_cursor_dep),
):
    """
    Halaman artist berdasarkan channel.
    """
    try:
        cursor, _ = db
        context = ArtistPresenter.channel(cursor, channel_id)
        context["request"] = request

        return templates.TemplateResponse(
            "music/artists/index.html",
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
                "message": "Gagal memuat artist untuk channel ini",
                "error": str(e),
            },
            status_code=500,
        )


# =====================================================
# CREATE
# =====================================================

@router.get(
    "/artists/create",
    response_class=HTMLResponse,
    summary="Create artist page",
    description="Halaman form tambah artist"
)
def create(
    request: Request,
):
    """
    Form tambah artist.
    """
    try:
        context = ArtistPresenter.create()
        context["request"] = request

        return templates.TemplateResponse(
            "music/artists/form.html",
            context,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "message": "Gagal memuat halaman tambah artist",
                "error": str(e),
            },
            status_code=500,
        )


# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/artists/{artist_id}",
    response_class=HTMLResponse,
    summary="Artist detail page",
    description="Halaman detail artist"
)
def detail(
    artist_id: int,
    request: Request,
):
    """
    Detail artist.
    """
    try:
        context = ArtistPresenter.detail(artist_id)
        context["request"] = request

        return templates.TemplateResponse(
            "music/artists/detail.html",
            context,
        )
    except ArtistNotFoundError as e:
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "message": str(e),
                "resource": "Artist",
                "resource_id": artist_id,
            },
            status_code=404,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "message": f"Gagal memuat detail artist ID: {artist_id}",
                "error": str(e),
            },
            status_code=500,
        )


# =====================================================
# EDIT
# =====================================================

@router.get(
    "/artists/{artist_id}/edit",
    response_class=HTMLResponse,
    summary="Edit artist page",
    description="Halaman form edit artist"
)
def edit(
    artist_id: int,
    request: Request,
):
    """
    Form edit artist.
    """
    try:
        context = ArtistPresenter.edit(artist_id)
        context["request"] = request

        return templates.TemplateResponse(
            "music/artists/form.html",
            context,
        )
    except ArtistNotFoundError as e:
        return templates.TemplateResponse(
            "errors/404.html",
            {
                "request": request,
                "message": str(e),
                "resource": "Artist",
                "resource_id": artist_id,
            },
            status_code=404,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "message": f"Gagal memuat halaman edit artist ID: {artist_id}",
                "error": str(e),
            },
            status_code=500,
        )

# =====================================================
# REDIRECTS
# =====================================================

@router.get(
    "/artists/{artist_id}/view",
    response_class=HTMLResponse,
)
def redirect_to_detail(
    artist_id: int,
):
    """
    Redirect to detail page.
    """
    return RedirectResponse(
        url=f"/admin/artists/{artist_id}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get(
    "/artists/{artist_id}/delete",
    response_class=HTMLResponse,
)
def redirect_to_delete(
    artist_id: int,
):
    """
    Redirect to delete action (handled by JS).
    """
    return RedirectResponse(
        url=f"/admin/artists/{artist_id}",
        status_code=status.HTTP_302_FOUND,
    )


# =====================================================
# ERROR PAGES
# =====================================================

@router.get(
    "/artists/error",
    response_class=HTMLResponse,
)
def error_page(
    request: Request,
    message: str = "Terjadi kesalahan",
    status_code: int = 400,
):
    """
    Halaman error generic.
    """
    return templates.TemplateResponse(
        "errors/generic.html",
        {
            "request": request,
            "message": message,
            "status_code": status_code,
        },
        status_code=status_code,
    )


@router.get(
    "/artists/not-found",
    response_class=HTMLResponse,
)
def not_found_page(
    request: Request,
    message: str = "Artist tidak ditemukan",
):
    """
    Halaman not found.
    """
    return templates.TemplateResponse(
        "errors/404.html",
        {
            "request": request,
            "message": message,
            "resource": "Artist",
        },
        status_code=404,
    )


# =====================================================
# EXPORT
# =====================================================

__all__ = ['router']