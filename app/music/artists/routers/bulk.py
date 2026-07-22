"""
Artist Bulk Router
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.music.artists.schema import (
    ArtistBulkDelete,
)

from app.music.services.artists.service import ArtistService

from app.music.services.artists.exceptions import (
    ArtistDatabaseError,
    ArtistHasSongsError,
    ArtistNotFoundError,
    BulkDeleteError,
    EmptySelectionError,
)

router = APIRouter()


# =====================================================
# BULK DELETE
# =====================================================

@router.delete("/bulk")
def bulk_delete(
    data: ArtistBulkDelete,
):
    """
    Bulk Delete Artist.
    """

    try:

        return ArtistService.bulk_delete(
            data.ids,
        )

    except EmptySelectionError as exc:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(exc),
            },
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

    except BulkDeleteError as exc:

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