"""
Songs Presenter
===============

Prepare template context untuk halaman Songs.

Presenter tidak mengandung query database
dan tidak mengandung business logic.
"""

from __future__ import annotations

from app.music.services.songs.filter import (
    available_filters,
)
from app.music.services.songs.statistics import (
    build_statistics,
)

from app.music.repositories.export.statistics import (
    get_export_information,
)
from app.music.repositories.export.types import (
    ExportInformation,
    ExportMode,
)


# ==========================================================
# INDEX CONTEXT
# ==========================================================


def build_index_context() -> dict:
    """
    Build context untuk halaman Songs.
    """

    return {
        "statistics": build_statistics(),
        "filters": available_filters(),
    }


# ==========================================================
# TABLE CONTEXT
# ==========================================================


def build_table_context() -> dict:
    """
    Build context untuk DataTable Songs.
    """

    return {
        "filters": available_filters(),
    }


# ==========================================================
# FORM CONTEXT
# ==========================================================


def build_form_context() -> dict:
    """
    Build context untuk form Create/Edit.
    """

    filters = available_filters()

    return {
        "artists": filters["artists"],
        "channels": filters["channels"],
        "statuses": filters["statuses"],
    }


# ==========================================================
# DETAIL CONTEXT
# ==========================================================


def build_detail_context(
    song: dict,
) -> dict:
    """
    Build context untuk halaman detail song.
    """

    return {
        "song": song,
    }


# ==========================================================
# DASHBOARD CONTEXT
# ==========================================================


def build_dashboard_context() -> dict:
    """
    Build dashboard context.
    """

    return {
        "statistics": build_statistics(),
    }


# ==========================================================
# EXPORT CONTEXT
# ==========================================================


def build_export_context(
    *,
    day: int,
    mode: ExportMode,
) -> dict:
    """
    Build template context.
    """

    info = get_export_information(
        day,
        mode,
    )

    return {
        "export": info,
        "day": day,
        "mode": mode,
    }


# ==========================================================
# EXPORT INFORMATION
# ==========================================================


def build_export_information(
    *,
    day: int,
    mode: ExportMode,
) -> ExportInformation:
    """
    Return export information.
    """

    return get_export_information(
        day,
        mode,
    )


# ==========================================================
# EXPORT STATUS
# ==========================================================


def build_export_status(
    *,
    day: int,
    mode: ExportMode,
) -> dict:
    """
    Build export status for UI.
    """

    info = get_export_information(
        day,
        mode,
    )

    return {
        "already_exported": info["already_exported"],
        "remaining": info["remaining"],
        "unique_songs": info["unique_songs"],
        "total_available": info["total_available"],
    }