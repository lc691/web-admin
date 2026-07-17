"""
Usage Service
=============

Main orchestrator untuk feature Usage.

Seluruh endpoint hanya berinteraksi
dengan service ini.
"""

from __future__ import annotations

from app.music.repositories.usage.types import (
    UsageBatch,
    UsageMode,
    UsageResult,
    UsageStatistics,
)

from .batches import (
    batch,
    batches,
)

from .songs import (
    count,
    songs,
)

from .statistics import (
    statistics,
)

from .delete import (
    delete,
)

from .reset import (
    reset,
)

# ==========================================================
# USAGE
# ==========================================================


def usage(
    *,
    day: int,
    mode: UsageMode,
) -> UsageResult | None:
    """
    Return usage information.
    """

    usage_batch = batch(
        day=day,
        mode=mode,
    )

    if usage_batch is None:
        return None

    usage_statistics = statistics(
        batch_id=usage_batch["id"],
    )

    usage_songs = songs(
        batch_id=usage_batch["id"],
    )

    return {
        "batch": usage_batch,
        "statistics": usage_statistics,
        "songs": usage_songs,
    }


# ==========================================================
# BATCHES
# ==========================================================


def usage_batches(
    *,
    mode: UsageMode,
) -> list[UsageBatch]:
    """
    Return export batches.
    """

    return batches(
        mode=mode,
    )


# ==========================================================
# STATISTICS
# ==========================================================


def usage_statistics(
    *,
    batch_id: int,
) -> UsageStatistics:
    """
    Return usage statistics.
    """

    return statistics(
        batch_id=batch_id,
    )

# ==========================================================
# DELETE
# ==========================================================

def delete_batch(
    *,
    day: int,
    mode: UsageMode,
):
    """
    Delete export batch.
    """

    return delete(
        day=day,
        mode=mode,
    )


# ==========================================================
# RESET
# ==========================================================

def reset_batches(
    *,
    mode: UsageMode,
):
    """
    Reset export batches.
    """

    return reset(
        mode=mode,
    )


# ==========================================================
# SONGS
# ==========================================================


def usage_songs(
    *,
    batch_id: int,
):
    """
    Return usage songs.
    """

    return songs(
        batch_id=batch_id,
    )


# ==========================================================
# COUNT
# ==========================================================


def usage_count(
    *,
    batch_id: int,
) -> int:
    """
    Return total songs.
    """

    return count(
        batch_id=batch_id,
    )