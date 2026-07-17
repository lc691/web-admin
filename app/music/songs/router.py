"""
Songs Router
============

HTTP endpoints untuk feature Songs.

Router hanya bertanggung jawab menerima request
dan mengembalikan response.

Seluruh business logic berada di Service Layer.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi import HTTPException
from fastapi import Query
from fastapi.responses import Response

from app.music.repositories.export.types import (
    ExportMode,
)

from app.music.repositories.songs.types import (
    CreateSong,
    SongStatus,
    UpdateSong,
)

from app.music.services.export.service import (
    export,
    status,
)

from app.music.services.songs import (
    service,
)

from app.music.services.songs.search import (
    build_response,
)

from app.music.services.usage import (
    service as usage_service,
)

from app.music.services.usage.types import (
    UsageMode,
)


router = APIRouter(
    prefix="/songs",
    tags=["Songs"],
)

# ==========================================================
# LIST
# ==========================================================


@router.get("")
def list_songs(
    request: Request,

    draw: int = Query(1),
    keyword: str | None = Query(None),
    channel_id: int | None = Query(None),
    artist_id: int | None = Query(None),
    status: SongStatus | None = Query(None),
    start: int = Query(0, ge=0),
    length: int = Query(25, ge=1, le=100),
    order_by: str = Query("s.id"),
    descending: bool = Query(True),
):
    print("=" * 60)
    print("QUERY PARAMS:", dict(request.query_params))
    print("KEYWORD:", keyword)

    filters = service.get_filters(
        keyword=keyword,
        channel_id=channel_id,
        artist_id=artist_id,
        status=status,
    )

    print("FILTERS :", filters)

    return build_response(
        draw=draw,
        filters=filters,
        start=start,
        length=length,
        order_by=order_by,
        descending=descending,
    )

# ==========================================================
# STATISTICS
# ==========================================================


@router.get("/statistics")
def statistics():
    """
    Song statistics.
    """

    return service.get_statistics()


# ==========================================================
# IMPORT
# ==========================================================


@router.post("/import")
def import_songs(
    payload: list[CreateSong],
):
    """
    Import songs.
    """

    return service.import_song_list(
        payload,
    )


# ==========================================================
# BULK STATUS
# ==========================================================


@router.patch("/bulk/status")
def bulk_status(
    song_ids: list[int],
    status: SongStatus,
):
    """
    Bulk update status.
    """

    return {
        "updated": service.bulk_update_song_status(
            song_ids,
            status,
        )
    }


# ==========================================================
# BULK ARTIST
# ==========================================================


@router.patch("/bulk/artist")
def bulk_artist(
    song_ids: list[int],
    artist_id: int,
):
    """
    Bulk update artist.
    """

    return {
        "updated": service.bulk_update_song_artist(
            song_ids,
            artist_id,
        )
    }


# ==========================================================
# BULK RELEASE DATE
# ==========================================================


@router.patch("/bulk/release-date")
def bulk_release_date(
    song_ids: list[int],
    release_date: str | None = None,
):
    """
    Bulk update release date.
    """

    return {
        "updated": service.bulk_update_song_release_date(
            song_ids,
            release_date,
        )
    }


# ==========================================================
# BULK DELETE
# ==========================================================


@router.delete("/bulk")
def bulk_delete(
    song_ids: list[int],
):
    """
    Bulk delete songs.
    """

    return {
        "deleted": service.bulk_delete_songs(
            song_ids,
        )
    }

# ==========================================================
# EXPORT PLAYLIST
# ==========================================================

@router.get(
    "/export/status",
    summary="Export status",
)
def export_status(
    mode: ExportMode = "normal",
):
    return status(
        mode=mode,
    )

@router.get(
    "/export/day/{day}",
    summary="Export playlist",
)
def export_playlist(
    day: int,
    mode: ExportMode = Query(
        default="normal",
        description="Export mode",
    ),
    target: int = Query(
        default=160,
        ge=1,
        le=1000,
        description="Final playlist size",
    ),
    duplicate: int = Query(
        default=2,
        ge=1,
        le=20,
        description="Duplicate count",
    ),
    channel_limit: int = Query(
        default=2,
        ge=1,
        description="Preferred channel limit",
    ),
    excluded_channels: list[int] = Query(
        default=[],
        description="Excluded channel ids",
    ),
) -> Response:
    """
    Export playlist as TXT.
    """

    text = export(
        day=day,
        mode=mode,
        target=target,
        duplicate=duplicate,
        channel_limit=channel_limit,
        excluded_channels=excluded_channels,
    )

    filename = f"{mode}_day_{day}.txt"

    return Response(
        content=text,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# ==========================================================
# USAGE BATCHES
# ==========================================================


@router.get(
    "/usage",
    summary="Usage batches",
)
def usage_batches(
    mode: UsageMode = "normal",
):
    """
    Return usage batches.
    """

    return usage_service.usage_batches(
        mode=mode,
    )


# ==========================================================
# USAGE
# ==========================================================


@router.get(
    "/usage/day/{day}",
    summary="Usage",
)
def usage(
    day: int,
    mode: UsageMode = "normal",
):
    """
    Return usage.
    """

    result = usage_service.usage(
        day=day,
        mode=mode,
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Export batch not found.",
        )

    return result

# ==========================================================
# DELETE USAGE
# ==========================================================


@router.delete(
    "/usage/day/{day}",
    summary="Delete usage batch",
)
def delete_usage(
    day: int,
    mode: UsageMode = "normal",
):
    """
    Delete export batch.
    """

    deleted = usage_service.delete_batch(
        day=day,
        mode=mode,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Export batch not found.",
        )

    return {
        "deleted": True,
        "day": day,
        "mode": mode,
    }

# ==========================================================
# RESET USAGE
# ==========================================================


@router.delete(
    "/usage",
    summary="Reset usage",
)
def reset_usage(
    mode: UsageMode = "normal",
):
    """
    Reset export batches.
    """

    deleted = usage_service.reset_batches(
        mode=mode,
    )

    return {
        "deleted": deleted,
        "mode": mode,
    }

# ==========================================================
# CREATE
# ==========================================================


@router.post("")
def create_song(
    payload: CreateSong,
):
    """
    Create song.
    """

    return service.create_song(
        payload,
    )

@router.get("/{song_id}")
def get_song(
    song_id: int,
):
    """
    Song detail.
    """

    from app.music.repositories.songs.songs import get_song

    song = get_song(song_id)

    if song is None:
        raise HTTPException(
            status_code=404,
            detail="Song not found.",
        )

    return song





# ==========================================================
# UPDATE
# ==========================================================


@router.put("/{song_id}")
def update_song(
    song_id: int,
    payload: UpdateSong,
):
    """
    Update song.
    """

    return service.update_song(
        song_id,
        payload,
    )


# ==========================================================
# DELETE
# ==========================================================


@router.delete("/{song_id}")
def delete_song(
    song_id: int,
):
    """
    Delete song.
    """

    return service.delete_song(
        song_id,
    )