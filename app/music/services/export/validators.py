"""
Export Validator
================

Validation helpers untuk proses export.

Validator tidak mengakses database dan tidak
mengandung business process.
"""

from __future__ import annotations

from app.music.repositories.export.types import ExportMode

# ==========================================================
# CONSTANTS
# ==========================================================

MIN_TARGET = 1
MAX_TARGET = 1000

MIN_DUPLICATE = 1
MAX_DUPLICATE = 20

MIN_CHANNEL_LIMIT = 1


# ==========================================================
# TARGET
# ==========================================================


def validate_target(
    target: int,
) -> None:
    """
    Validate export target.
    """

    if target < MIN_TARGET:
        raise ValueError(
            f"Target must be >= {MIN_TARGET}."
        )

    if target > MAX_TARGET:
        raise ValueError(
            f"Target must be <= {MAX_TARGET}."
        )


# ==========================================================
# DUPLICATE
# ==========================================================


def validate_duplicate(
    duplicate: int,
) -> None:
    """
    Validate duplicate count.
    """

    if duplicate < MIN_DUPLICATE:
        raise ValueError(
            f"Duplicate must be >= {MIN_DUPLICATE}."
        )

    if duplicate > MAX_DUPLICATE:
        raise ValueError(
            f"Duplicate must be <= {MAX_DUPLICATE}."
        )


# ==========================================================
# CHANNEL LIMIT
# ==========================================================


def validate_channel_limit(
    channel_limit: int,
) -> None:
    """
    Validate preferred channel limit.
    """

    if channel_limit < MIN_CHANNEL_LIMIT:
        raise ValueError(
            "Channel limit must be >= 1."
        )


# ==========================================================
# DAY
# ==========================================================


def validate_day(
    day: int,
) -> None:
    """
    Validate export day.
    """

    if day < 1:
        raise ValueError(
            "Day must be >= 1."
        )


# ==========================================================
# MODE
# ==========================================================


def validate_mode(
    mode: ExportMode,
) -> None:
    """
    Validate export mode.
    """

    if mode not in (
        "normal",
        "clean",
        "blacklist",
    ):
        raise ValueError(
            f"Invalid export mode: {mode}"
        )


# ==========================================================
# EXPORT REQUEST
# ==========================================================


def validate_export_request(
    *,
    day: int,
    mode: ExportMode,
    target: int,
    duplicate: int,
    channel_limit: int,
) -> None:
    """
    Validate export request.
    """

    validate_day(day)
    validate_mode(mode)
    validate_target(target)
    validate_duplicate(duplicate)
    validate_channel_limit(channel_limit)


# ==========================================================
# TARGET UNIQUE
# ==========================================================


def calculate_target_unique(
    *,
    target: int,
    duplicate: int,
) -> int:
    """
    Calculate required unique songs.

    Example

        target = 140
        duplicate = 2

        result = 70
    """

    return (target + duplicate - 1) // duplicate