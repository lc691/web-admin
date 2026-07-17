"""
Usage Reset Service
===================

Business logic untuk reset seluruh export batch.
"""

from __future__ import annotations

from app.music.repositories.usage.reset import (
    reset_mode,
)

from .types import (
    UsageMode,
)

# ==========================================================
# RESET
# ==========================================================


def reset(
    *,
    mode: UsageMode,
) -> int:
    """
    Reset export batches.
    """

    return reset_mode(
        mode=mode,
    )