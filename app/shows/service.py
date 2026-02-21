from typing import Dict, List, Optional

from .repository import ShowRepository

_repo = ShowRepository()


# =====================================================
# READ
# =====================================================


def list_shows() -> List[Dict]:
    return _repo.list_all()


def get_show(show_id: int) -> Optional[Dict]:
    if not isinstance(show_id, int) or show_id <= 0:
        return None
    return _repo.get_by_id(show_id)


# =====================================================
# CREATE
# =====================================================


def create_show(data: Dict) -> int:
    """
    Create new show.
    Returns affected row count.
    """
    if not data or not data.get("title"):
        raise ValueError("Judul wajib diisi")

    return _repo.insert(data)


# =====================================================
# UPDATE
# =====================================================


def update_show(show_id: int, data: Dict) -> int:
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

    return affected


# =====================================================
# BULK UPDATE
# =====================================================


def bulk_update_shows(ids: List[int], data: Dict) -> int:
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

    return affected


def bulk_update_shows_safe(ids: list[int], data: Dict) -> int:
    if not ids:
        raise ValueError("IDs kosong")

    if len(ids) > 500:
        raise ValueError("Bulk update terlalu besar")

    affected = _repo.update_bulk(ids, data)

    if affected != len(ids):
        raise ValueError("Beberapa show tidak ditemukan")

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

    affected = _repo.delete(show_id)

    if affected == 0:
        raise ValueError("Show tidak ditemukan")

    return affected
