"""
Usage Batch Service
===================

Business logic untuk
export batch.
"""

from __future__ import annotations

from app.music.repositories.usage.batches import (
    get_batch,
    get_batches,
)

from .types import (
    UsageBatch,
    UsageMode,
)

# ==========================================================
# BATCH
# ==========================================================


def batch(
    *,
    day: int,
    mode: UsageMode,
) -> UsageBatch | None:
    """
    Return export batch.
    """

    return get_batch(
        day=day,
        mode=mode,
    )


# ==========================================================
# BATCHES
# ==========================================================


def batches(
    *,
    mode: UsageMode,
) -> list[UsageBatch]:
    """
    Return export batches.
    """

    return get_batches(
        mode=mode,
    )