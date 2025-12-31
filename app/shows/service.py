from typing import Dict, List, Optional

from .repository import ShowRepository

_repo = ShowRepository()


def list_shows() -> List[Dict]:
    return _repo.list_all()


def get_show(show_id: int) -> Optional[Dict]:
    return _repo.get_by_id(show_id)


def create_show(data: Dict) -> None:
    _repo.insert(data)


def update_show(show_id: int, data: Dict) -> None:
    _repo.update(show_id, data)


def delete_show(show_id: int) -> None:
    _repo.delete(show_id)
