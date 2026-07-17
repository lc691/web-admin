"""
Usage Delete Service
====================

Business logic untuk menghapus satu export batch.
"""

from __future__ import annotations

from app.music.repositories.usage.batches import (
    get_batch,
)

from app.music.repositories.usage.delete import (
    delete_batch,
)

from .types import (
    UsageMode,
)

# ==========================================================
# DELETE
# ==========================================================


def delete(
    *,
    day: int,
    mode: UsageMode,
) -> bool:
    """
    Delete export batch.
    """

    batch = get_batch(
        day=day,
        mode=mode,
    )

    if batch is None:

        return False

    return delete_batch(
        day=day,
        mode=mode,
    )