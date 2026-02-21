from typing import Dict, List

from app.repositories.show_files_repo import (
    delete_show_files_bulk,
    get_show_file,
    list_show_files,
    update_show_file,
    update_show_files_bulk,
)

# =========================
# READ
# =========================


def list_show_files_service() -> List[Dict]:
    return list_show_files()


def get_show_file_service(show_file_id: int) -> Dict | None:
    if not isinstance(show_file_id, int) or show_file_id <= 0:
        return None

    return get_show_file(show_file_id)


# =========================
# UPDATE SINGLE
# =========================


def update_show_file_service(show_file_id: int, data: Dict) -> int:
    """
    Update single show_file.
    Returns affected row count.
    """

    if not isinstance(show_file_id, int) or show_file_id <= 0:
        return 0

    if not data:
        return 0

    return update_show_file(show_file_id, data)


# =========================
# UPDATE BULK
# =========================


def update_show_files_bulk_service(ids: List[int], data: Dict) -> int:
    """
    Update multiple show_files.
    Returns affected row count.
    """

    if not ids:
        return 0

    if not data:
        return 0

    return update_show_files_bulk(ids, data)


# =========================
# DELETE BULK
# =========================
def delete_show_files_bulk_service(ids: List[int]) -> int:
    if not ids:
        return 0

    return delete_show_files_bulk(ids)
