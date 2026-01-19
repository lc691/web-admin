from app.repositories.show_files_repo import get_show_file, list_show_files, update_show_file


def list_show_files_service():
    return list_show_files()


def get_show_file_service(show_file_id: int):
    return get_show_file(show_file_id)


def update_show_file_service(show_file_id: int, show_id: int | None, message_id: int | None):
    return update_show_file(show_file_id, show_id, message_id)
