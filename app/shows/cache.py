import time
from typing import Any


class ShowCache:
    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self._store: dict[str, dict] = {}

    def get(self, key: str):
        item = self._store.get(key)
        if not item:
            return None
        if time.time() - item["ts"] > self.ttl:
            self._store.pop(key, None)
            return None
        return item["val"]

    def set(self, key: str, value: Any):
        self._store[key] = {"val": value, "ts": time.time()}

    def clear(self, prefix: str):
        for k in list(self._store):
            if k.startswith(prefix):
                self._store.pop(k, None)
