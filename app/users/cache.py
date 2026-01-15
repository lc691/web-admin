class UserCache:
    def __init__(self):
        self._list = {}
        self._by_id = {}

    def get_list(self, key: str):
        return self._list.get(key)

    def set_list(self, key: str, data):
        self._list[key] = data

    def get(self, user_id: int):
        return self._by_id.get(user_id)

    def set(self, user_id: int, data):
        self._by_id[user_id] = data

    def clear(self, user_id: int | None = None):
        self._list.clear()
        if user_id:
            self._by_id.pop(user_id, None)
