from .repository import FileRepository

_repo = FileRepository()


def list_files() -> list[dict]:
    return _repo.list_all_with_show_files()


def get_file(file_id: int) -> dict | None:
    return _repo.get_by_id(file_id)


def create_file(**kwargs) -> int:
    return _repo.insert(**kwargs)


def update_file(file_id: int, **kwargs) -> None:
    _repo.update_full(file_id=file_id, **kwargs)


def delete_file(file_id: int) -> None:
    _repo.delete(file_id)
