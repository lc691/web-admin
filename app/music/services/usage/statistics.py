"""
Usage Statistics Service
========================

Business logic untuk
Usage Statistics.
"""

from __future__ import annotations

from app.music.repositories.usage.statistics import (
    get_statistics,
)

from .types import (
    UsageStatistics,
)

# ==========================================================
# STATISTICS
# ==========================================================


def statistics(
    *,
    batch_id: int,
) -> UsageStatistics:
    """
    Return usage statistics.
    """

    return get_statistics(
        batch_id=batch_id,
    )