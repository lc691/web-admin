import logging
from typing import Dict, List, Optional

from .repository import AdminRepository

logger = logging.getLogger(__name__)
repo = AdminRepository()


# =========================
# CRUD OPERATIONS
# =========================

def list_admins(only_active: bool = False) -> List[Dict]:
    """Get all admins."""
    return repo.list_all(only_active=only_active)


def get_admin(user_id: int) -> Optional[Dict]:
    """Get admin by user_id."""
    return repo.get_by_id(user_id)


def get_admin_by_username(username: str) -> Optional[Dict]:
    """Get admin by username."""
    return repo.get_by_username(username)


def create_admin(
    user_id: int,
    first_name: str,
    username: str,
    is_active: bool = True,
) -> Dict:
    """Create new admin."""
    # Cek duplikat
    existing = repo.get_by_id(user_id)
    if existing:
        raise ValueError(f"Admin dengan user_id {user_id} sudah ada")

    logger.info(f"Creating admin: {first_name} (user_id: {user_id})")
    result = repo.create(user_id, first_name, username, is_active)
    logger.info(f"Admin {first_name} created successfully")
    return result


def update_admin(
    user_id: int,
    first_name: Optional[str] = None,
    username: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Dict:
    """Update admin."""
    # Cek apakah admin ada
    existing = repo.get_by_id(user_id)
    if not existing:
        raise ValueError(f"Admin dengan user_id {user_id} tidak ditemukan")

    # Cek duplikat username (jika diubah)
    if username is not None:
        existing_username = repo.get_by_username(username)
        if existing_username and existing_username["user_id"] != user_id:
            raise ValueError(f"Username {username} sudah digunakan oleh admin lain")

    logger.info(f"Updating admin: user_id={user_id}")
    result = repo.update(user_id, first_name, username, is_active)
    logger.info(f"Admin {user_id} updated successfully")
    return result


def delete_admin(user_id: int) -> bool:
    """Delete admin."""
    existing = repo.get_by_id(user_id)
    if not existing:
        raise ValueError(f"Admin dengan user_id {user_id} tidak ditemukan")

    logger.info(f"Deleting admin: user_id={user_id}")
    result = repo.delete(user_id)
    logger.info(f"Admin {user_id} deleted successfully")
    return result


def activate_admin(user_id: int) -> Dict:
    """Activate admin."""
    return update_admin(user_id, is_active=True)


def deactivate_admin(user_id: int) -> Dict:
    """Deactivate admin."""
    return update_admin(user_id, is_active=False)


def count_admins(only_active: bool = False) -> int:
    """Count admins."""
    return repo.count(only_active=only_active)


def admin_exists(user_id: int) -> bool:
    """Check if admin exists."""
    return repo.exists(user_id)