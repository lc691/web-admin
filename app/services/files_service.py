from fastapi import HTTPException

from app.repositories.files_repo import (
    delete_file,
    get_file,
    get_file_usage_count,
    list_files,
    update_file,
)


def list_files_service():
    return list_files()


def get_file_service(file_id: int):
    return get_file(file_id)


def update_file_service(file_id: int, payload: dict):
    return update_file(file_id, payload)


def delete_file_service(file_id: int):
    usage = get_file_usage_count(file_id)

    if usage > 0:
        raise HTTPException(status_code=400, detail=f"File masih dipakai oleh {usage} show")

    delete_file(file_id)
