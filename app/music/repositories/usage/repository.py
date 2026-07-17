"""
Usage Repository
================

Facade repository untuk feature Usage.
"""

from __future__ import annotations

from .batches import (
    get_batch,
    get_batches,
)

from .songs import (
    get_usage_songs,
)

from .statistics import (
    get_statistics,
)

from .types import (
    UsageMode,
    UsageResult,
)

# ==========================================================
# GET USAGE
# ==========================================================


def get_usage(
    *,
    day: int,
    mode: UsageMode,
) -> UsageResult | None:
    """
    Return complete usage information.
    """

    batch = get_batch(
        day=day,
        mode=mode,
    )

    if batch is None:
        return None

    songs = get_usage_songs(
        batch_id=batch["id"],
    )

    statistics = get_statistics(
        batch_id=batch["id"],
    )

    return {
        "batch": batch,
        "statistics": statistics,
        "songs": songs,
    }


# ==========================================================
# GET BATCHES
# ==========================================================


def get_usage_batches(
    *,
    mode: UsageMode,
):
    """
    Return export batches.
    """

    return get_batches(
        mode=mode,
    )