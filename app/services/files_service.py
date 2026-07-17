import logging
from typing import Dict, List, Optional

from ..repositories.files_repo import FileRepository

logger = logging.getLogger(__name__)
repo = FileRepository()


# ==========================================================
# LIST WITH PAGINATION
# ==========================================================
def list_files_service(
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    show_id: int | None = None,
    file_type: str | None = None,
    is_paid: bool | None = None,
) -> dict:
    """
    Get files with pagination and filters.
    """
    return repo.list_all(
        page=page,
        per_page=per_page,
        search=search,
        show_id=show_id,
        file_type=file_type,
        is_paid=is_paid,
    )


def list_files_simple_service(
    show_id: int | None = None,
) -> List[Dict]:
    """
    Get all files without pagination (for dropdown/exports).
    """
    return repo.list_simple(show_id=show_id)


# ==========================================================
# GET BY ID
# ==========================================================
def get_file_service(file_id: int) -> Optional[Dict]:
    """Get file by ID."""
    return repo.get_by_id(file_id)


def get_files_by_show_service(show_id: int) -> List[Dict]:
    """Get files by show ID."""
    return repo.get_by_show_id(show_id)


# ==========================================================
# CREATE
# ==========================================================
def create_file_service(data: dict) -> Dict:
    """Create new file."""
    if not data.get("file_name"):
        raise ValueError("file_name is required")

    logger.info(f"Creating file: {data.get('file_name')}")
    result = repo.create(data)
    logger.info(f"File created: {result.get('id')}")
    return result


# ==========================================================
# UPDATE
# ==========================================================
def update_file_service(file_id: int, data: dict) -> Dict:
    """Update file."""
    existing = repo.get_by_id(file_id)
    if not existing:
        raise ValueError(f"File dengan ID {file_id} tidak ditemukan")

    logger.info(f"Updating file: {file_id}")
    result = repo.update(file_id, data)
    logger.info(f"File {file_id} updated")
    return result


# ==========================================================
# DELETE
# ==========================================================
def delete_file_service(file_id: int) -> bool:
    """Delete file."""
    existing = repo.get_by_id(file_id)
    if not existing:
        raise ValueError(f"File dengan ID {file_id} tidak ditemukan")

    logger.info(f"Deleting file: {file_id}")
    result = repo.delete(file_id)
    logger.info(f"File {file_id} deleted")
    return result


# ==========================================================
# BULK DELETE
# ==========================================================
def bulk_delete_files_service(file_ids: list[int]) -> int:
    """Delete multiple files."""
    if not file_ids:
        return 0

    logger.info(f"Bulk deleting {len(file_ids)} files")
    result = repo.bulk_delete(file_ids)
    logger.info(f"{result} files deleted")
    return result


# ==========================================================
# SYNC SHOW FILES
# ==========================================================
def sync_show_files_service(show_id: int) -> int:
    """Sync files to show_files table."""
    logger.info(f"Syncing files for show {show_id}")
    result = repo.sync_show_files(show_id)
    logger.info(f"Synced {result} files for show {show_id}")
    return result


# ==========================================================
# STATS
# ==========================================================
def get_file_stats_service() -> dict:
    """Get file statistics."""
    return repo.get_stats()


def get_file_usage_count_service(file_id: int) -> int:
    """Get usage count of a file."""
    return repo.get_usage_count(file_id)