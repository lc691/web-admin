"""
Export Service
==============

Business orchestration untuk proses export playlist.

Flow

1. Validate request
2. Hitung target_unique
3. Cek batch
4. Existing batch
   - Load songs
   - Shuffle
5. New batch
   - Cek remaining
   - Reset usage bila perlu
   - Load available songs
   - Selector
   - Save usage
   - Create batch
   - Save batch items
   - Complete batch
6. Duplicate
7. Formatter
8. Return TXT
"""

from __future__ import annotations

import random

from app.music.repositories.export.batches import (
    complete_export_batch,
    create_export_batch,
    create_export_batch_items,
    get_export_batch_by_day,
)
from app.music.repositories.export.songs import (
    get_available_songs,
    get_exported_songs,
)
from app.music.repositories.export.statistics import (
    export_exists,
    get_remaining_song_count,
)
from app.music.repositories.export.types import (
    ExportMode,
)
from app.music.repositories.export.usage import (
    reset_song_usage,
    save_song_usage,
)

from .status import get_status

from .duplicate import duplicate_songs
from .formatter import build_txt
from .selector import select_songs
from .validators import (
    calculate_target_unique,
    validate_export_request,
)

# ==========================================================
# EXPORT
# ==========================================================


def export(
    *,
    day: int,
    mode: ExportMode,
    target: int,
    duplicate: int,
    channel_limit: int,
    excluded_channels: list[int] | None = None,
) -> str:
    """
    Export playlist.
    """

    validate_export_request(
        day=day,
        mode=mode,
        target=target,
        duplicate=duplicate,
        channel_limit=channel_limit,
    )

    target_unique = calculate_target_unique(
        target=target,
        duplicate=duplicate,
    )

    excluded_channels = excluded_channels or []

    if export_exists(
        day,
        mode,
    ):
        songs = load_existing_batch(
            day,
            mode,
        )

    else:
        songs = create_new_batch(
            day=day,
            mode=mode,
            target_unique=target_unique,
            target=target,
            duplicate=duplicate,
            channel_limit=channel_limit,
            excluded_channels=excluded_channels,
        )

    songs = duplicate_songs(
        songs,
        target=target,
        duplicate=duplicate,
    )

    return build_txt(songs)


# ==========================================================
# LOAD EXISTING
# ==========================================================


def load_existing_batch(
    day: int,
    mode: ExportMode,
):
    """
    Load existing export batch.
    """

    batch = get_export_batch_by_day(
        day,
        mode,
    )

    songs = get_exported_songs(
        batch["id"],
    )

    random.shuffle(songs)

    return songs


# ==========================================================
# CREATE NEW
# ==========================================================


def create_new_batch(
    *,
    day: int,
    mode: ExportMode,
    target_unique: int,
    target: int,
    duplicate: int,
    channel_limit: int,
    excluded_channels: list[int],
):
    """
    Create new export batch.
    """

    remaining = get_remaining_song_count(
        mode,
    )

    if remaining < target_unique:
        reset_song_usage(mode)

    songs = get_available_songs(
        mode=mode,
        exclude_channel_ids=excluded_channels,
    )

    selected = select_songs(
        songs,
        target=target_unique,
        preferred_channel_limit=channel_limit,
    )

    save_song_usage(
        selected,
        mode,
        day,
    )

    batch_id = create_export_batch(
        day=day,
        mode=mode,
        target=target,
        duplicate=duplicate,
        channel_limit=channel_limit,
        selected_unique=len(selected),
        excluded_channels=excluded_channels,
    )

    create_export_batch_items(
        batch_id,
        selected,
    )

    complete_export_batch(
        batch_id,
    )

    return selected

# ==========================================================
# STATUS
# ==========================================================

def status(
    *,
    mode: ExportMode,
):
    """
    Return export status.
    """

    return get_status(
        mode=mode,
    )