from app.repositories.files_repo import (
    delete_file,
    get_file,
    list_files,
    sync_show_files_by_show_id,
    update_file,
)


def list_files_service():
    return list_files()


def get_file_service(file_id: int):
    return get_file(file_id)


def update_file_service(file_id: int, payload: dict):
    return update_file(file_id, payload)


def delete_file_service(file_id: int):
    return delete_file(file_id)


def sync_show_files_service(show_id: int) -> int:
    result = sync_show_files_by_show_id(show_id)

    if result == -1:
        raise ValueError("Show tidak ditemukan")

    return result
