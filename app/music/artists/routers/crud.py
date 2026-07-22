"""
Artist CRUD Router
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.music.artists.schema import (
    ArtistCreate,
    ArtistUpdate,
    ArtistResponse,
)

from app.music.services.artists.service import ArtistService

from app.music.services.artists.exceptions import (
    ArtistAlreadyExistsError,
    ArtistDatabaseError,
    ArtistDeleteError,
    ArtistHasSongsError,
    ArtistNotFoundError,
    InvalidArtistNameError,
    InvalidChannelError,
)

router = APIRouter()

# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/{artist_id}",
    response_model=ArtistResponse,
)
def detail(
    artist_id: int,
):
    """
    Detail Artist.
    """

    try:

        return ArtistService.get_detail(
            artist_id,
        )

    except ArtistNotFoundError as exc:

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    except ArtistDatabaseError as exc:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )

# =====================================================
# CREATE
# =====================================================

@router.post(
    "/",
    response_model=ArtistResponse,
)
def create(
    data: ArtistCreate,
):
    """
    Create Artist.
    """

    try:

        return ArtistService.create(
            channel_id=data.channel_id,
            name=data.name,
        )

    except (
        ArtistAlreadyExistsError,
        InvalidArtistNameError,
        InvalidChannelError,
    ) as exc:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    except ArtistDatabaseError as exc:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )




# =====================================================
# UPDATE
# =====================================================

@router.put(
    "/{artist_id}",
    response_model=ArtistResponse,
)
def update(
    artist_id: int,
    data: ArtistUpdate,
):
    """
    Update Artist.
    """

    try:

        return ArtistService.update(
            artist_id=artist_id,
            channel_id=data.channel_id,
            name=data.name,
        )

    except ArtistNotFoundError as exc:

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    except (
        ArtistAlreadyExistsError,
        InvalidArtistNameError,
        InvalidChannelError,
    ) as exc:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    except ArtistDatabaseError as exc:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )


# =====================================================
# DELETE
# =====================================================

@router.delete(
    "/{artist_id}",
)
def delete(
    artist_id: int,
):
    """
    Delete Artist.
    """

    try:

        return ArtistService.delete(
            artist_id,
        )

    except ArtistNotFoundError as exc:

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    except ArtistHasSongsError as exc:

        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    except ArtistDeleteError as exc:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(exc),
            },
        )

    except ArtistDatabaseError as exc:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )