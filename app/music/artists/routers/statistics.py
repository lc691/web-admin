"""
Artist Statistics Router
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.music.services.artists.service import ArtistService
from app.music.services.artists.exceptions import (
    ArtistDatabaseError,
)

router = APIRouter()


# =====================================================
# DASHBOARD
# =====================================================

@router.get("/statistics")
def statistics(
    channel_id: int | None = Query(None),
):
    """
    Dashboard statistik artist.
    """

    try:
        return ArtistService.statistics(
            channel_id=channel_id,
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
# TOTAL ARTISTS
# =====================================================

@router.get("/statistics/total-artists")
def total_artists(
    channel_id: int | None = Query(None),
):
    """
    Total artist.
    """

    try:
        return {
            "total": ArtistService.total_artists(
                channel_id,
            )
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )


# =====================================================
# TOTAL SONGS
# =====================================================

@router.get("/{artist_id}/statistics/songs")
def total_songs(
    artist_id: int,
):
    """
    Total lagu artist.
    """

    try:
        return {
            "total": ArtistService.total_songs(
                artist_id,
            )
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )


# =====================================================
# SONG STATUS
# =====================================================

@router.get("/{artist_id}/statistics/status")
def song_status(
    artist_id: int,
):
    """
    Statistik status lagu.
    """

    try:
        return ArtistService.song_status(
            artist_id,
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
# ACTIVE CHANNELS
# =====================================================

@router.get("/statistics/active-channels")
def active_channels():
    """
    Channel yang memiliki artist.
    """

    try:
        return {
            "total": ArtistService.active_channels()
        }

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )


# =====================================================
# CHANNEL SUMMARY
# =====================================================

@router.get("/statistics/channel/{channel_id}")
def channel_summary(
    channel_id: int,
):
    """
    Ringkasan artist per channel.
    """

    try:
        return ArtistService.channel_summary(
            channel_id,
        )

    except ArtistDatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
            },
        )