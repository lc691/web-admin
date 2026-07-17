"""
Songs Validator
===============

Validation helpers untuk feature Songs.

Validator tidak mengakses database dan tidak
mengandung query SQL.
"""

from __future__ import annotations

from app.music.repositories.songs.types import (
    CreateSong,
    SongStatus,
    UpdateSong,
)

# ==========================================================
# CONSTANTS
# ==========================================================

MAX_TITLE_LENGTH = 255

VALID_STATUSES: tuple[SongStatus, ...] = (
    "Live",
    "Review",
    "Approved",
)

# ==========================================================
# TITLE
# ==========================================================


def validate_title(
    title: str,
) -> None:
    """
    Validate song title.
    """

    title = title.strip()

    if not title:
        raise ValueError(
            "Title is required."
        )

    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError(
            f"Title must not exceed {MAX_TITLE_LENGTH} characters."
        )


# ==========================================================
# ARTIST
# ==========================================================


def validate_artist_id(
    artist_id: int,
) -> None:
    """
    Validate artist id.
    """

    if artist_id <= 0:
        raise ValueError(
            "Invalid artist."
        )


# ==========================================================
# STATUS
# ==========================================================


def validate_status(
    status: SongStatus,
) -> None:
    """
    Validate song status.
    """

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status: {status}"
        )


# ==========================================================
# SONG ID
# ==========================================================


def validate_song_id(
    song_id: int,
) -> None:
    """
    Validate song id.
    """

    if song_id <= 0:
        raise ValueError(
            "Invalid song."
        )


# ==========================================================
# CREATE
# ==========================================================


def validate_create_song(
    data: CreateSong,
) -> None:
    """
    Validate create payload.
    """

    validate_artist_id(
        data["artist_id"],
    )

    validate_title(
        data["title"],
    )

    validate_status(
        data["status"],
    )


# ==========================================================
# UPDATE
# ==========================================================


def validate_update_song(
    song_id: int,
    data: UpdateSong,
) -> None:
    """
    Validate update payload.
    """

    validate_song_id(
        song_id,
    )

    validate_artist_id(
        data["artist_id"],
    )

    validate_title(
        data["title"],
    )

    validate_status(
        data["status"],
    )


# ==========================================================
# DELETE
# ==========================================================


def validate_delete_song(
    song_id: int,
) -> None:
    """
    Validate delete request.
    """

    validate_song_id(
        song_id,
    )


# ==========================================================
# BULK
# ==========================================================


def validate_bulk_song_ids(
    song_ids: list[int],
) -> None:
    """
    Validate bulk operation.
    """

    if not song_ids:
        raise ValueError(
            "No songs selected."
        )

    for song_id in song_ids:
        validate_song_id(song_id)
