import logging
from .repository import ShowRepository

logger = logging.getLogger(__name__)
_repo = ShowRepository()


# =====================================================
# READ (DENGAN PAGINATION)
# =====================================================

def list_shows(
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    include_stats: bool = True,
) -> dict:
    """
    Get shows with pagination.
    
    Args:
        page: Halaman (default: 1)
        per_page: Jumlah per halaman (default: 20)
        search: Keyword pencarian (optional)
        include_stats: Sertakan file stats (default: True)
    
    Returns:
        {
            "data": list[dict],
            "total": int,
            "page": int,
            "per_page": int,
            "total_pages": int
        }
    """
    if include_stats:
        return _repo.list_all(page, per_page, search)
    else:
        return _repo.list_all_simple(page, per_page, search)

# =====================================================
# LEGACY (TANPA PAGINATION - HATI-HATI)
# =====================================================

def list_all_shows() -> list[dict]:
    """
    ⚠️ DEPRECATED: Get ALL shows tanpa pagination.
    Hanya untuk keperluan export atau total kecil.
    """
    result = _repo.list_all(page=1, per_page=999999)
    return result["data"]


def get_show(show_id: int) -> dict | None:
    """Get single show by ID."""
    if not isinstance(show_id, int) or show_id <= 0:
        return None
    return _repo.get_by_id(show_id)


def search_shows(keyword: str, limit: int = 50) -> list[dict]:
    """
    Search shows by title or genre.
    """
    if not keyword or len(keyword.strip()) < 2:
        raise ValueError("Keyword minimal 2 karakter")
    
    return _repo.search(keyword.strip(), limit)


# =====================================================
# CREATE
# =====================================================

def create_show(data: dict) -> int:
    """
    Create new show.
    Returns affected row count.
    """
    if not data or not data.get("title"):
        raise ValueError("Judul wajib diisi")
    
    logger.info(f"Creating show: {data.get('title')}")
    result = _repo.insert(data)
    logger.info(f"Show created with ID: {result}")
    return result


# =====================================================
# UPDATE
# =====================================================

def update_show(show_id: int, data: dict) -> int:
    """
    Update single show.
    Raises error if not found.
    """
    if not isinstance(show_id, int) or show_id <= 0:
        raise ValueError("ID tidak valid")

    if not data:
        return 0

    if "title" in data and not data["title"]:
        raise ValueError("Judul tidak boleh kosong")

    affected = _repo.update_one(show_id, data)

    if affected == 0:
        raise ValueError("Show tidak ditemukan")

    logger.info(f"Show {show_id} updated: {data.keys()}")
    return affected


# =====================================================
# BULK UPDATE
# =====================================================

def bulk_update_shows(ids: list[int], data: dict) -> int:
    """
    Update multiple shows.
    Raises error if any id not found.
    """
    if not ids:
        raise ValueError("IDs kosong")

    if not data:
        return 0

    if len(ids) > 500:
        raise ValueError("Bulk update terlalu besar (max 500)")

    # sanitize ids
    ids = [i for i in ids if isinstance(i, int) and i > 0]
    if not ids:
        raise ValueError("IDs tidak valid")

    affected = _repo.update_bulk(ids, data)

    if affected != len(ids):
        raise ValueError("Beberapa show tidak ditemukan")

    logger.info(f"Bulk update: {affected} shows updated")
    return affected


# =====================================================
# DELETE
# =====================================================

def delete_show(show_id: int) -> int:
    """
    Delete show.
    Raises error if not found.
    """
    if not isinstance(show_id, int) or show_id <= 0:
        raise ValueError("ID tidak valid")

    # Cek dulu apakah show ada
    existing = _repo.get_by_id(show_id)
    if not existing:
        raise ValueError("Show tidak ditemukan")

    affected = _repo.delete(show_id)

    logger.info(f"Show {show_id} deleted: {existing.get('title')}")
    return affected


# =====================================================
# STATS
# =====================================================

def get_shows_stats() -> dict:
    """
    Get statistics for dashboard.
    """
    return _repo.get_stats()


# =====================================================
# EXPORT
# =====================================================

def export_shows_to_csv(ids: list[int] | None = None) -> str:
    """
    Export shows to CSV format.
    """
    if ids:
        shows = [_repo.get_by_id(i) for i in ids if i > 0]
        shows = [s for s in shows if s]
    else:
        shows = _repo.list_all()
    
    if not shows:
        return "No data"
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=shows[0].keys())
    writer.writeheader()
    writer.writerows(shows)
    
    return output.getvalue()