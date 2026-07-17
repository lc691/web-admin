"""
Export Song Selector
====================

Business logic untuk memilih lagu export.

Algorithm:
1. Group by channel
2. Preferred Channel Limit (Round Robin)
3. Adaptive Fill
"""

from __future__ import annotations

from collections import defaultdict

from app.music.repositories.export.types import SongRow


# ==========================================================
# GROUP BY CHANNEL
# ==========================================================


def group_by_channel(
    songs: list[SongRow],
) -> dict[int, list[SongRow]]:
    """
    Group songs by channel.
    """

    grouped: dict[int, list[SongRow]] = defaultdict(list)

    for song in songs:
        grouped[song["channel_id"]].append(song)

    return dict(grouped)


# ==========================================================
# ROUND ROBIN
# ==========================================================


def select_round_robin(
    grouped: dict[int, list[SongRow]],
    *,
    target: int,
    preferred_channel_limit: int,
) -> list[SongRow]:
    """
    Phase 1.

    Distribute songs fairly across channels.

    Each channel may contribute up to
    preferred_channel_limit songs.
    """

    selected: list[SongRow] = []

    channel_counts = {
        channel_id: 0
        for channel_id in grouped
    }

    while len(selected) < target:

        added = False

        for channel_id, songs in grouped.items():

            if len(selected) >= target:
                break

            if channel_counts[channel_id] >= preferred_channel_limit:
                continue

            if not songs:
                continue

            selected.append(songs.pop(0))

            channel_counts[channel_id] += 1

            added = True

        if not added:
            break

    return selected


# ==========================================================
# FILL REMAINING
# ==========================================================


def fill_remaining(
    grouped: dict[int, list[SongRow]],
    selected: list[SongRow],
    *,
    target: int,
) -> list[SongRow]:
    """
    Phase 2.

    Ignore preferred channel limit.

    Continue taking songs from any channel
    until target is reached.
    """

    if len(selected) >= target:
        return selected

    while len(selected) < target:

        added = False

        for songs in grouped.values():

            if len(selected) >= target:
                break

            if not songs:
                continue

            selected.append(songs.pop(0))

            added = True

        if not added:
            break

    return selected


# ==========================================================
# SELECT SONGS
# ==========================================================


def select_songs(
    songs: list[SongRow],
    *,
    target: int,
    preferred_channel_limit: int,
) -> list[SongRow]:
    """
    Select songs using the export algorithm.

    Phase 1
        Preferred Channel Limit

    Phase 2
        Adaptive Fill
    """

    grouped = group_by_channel(songs)

    selected = select_round_robin(
        grouped,
        target=target,
        preferred_channel_limit=preferred_channel_limit,
    )

    return fill_remaining(
        grouped,
        selected,
        target=target,
    )