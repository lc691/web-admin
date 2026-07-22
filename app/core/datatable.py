"""
Reusable DataTables Helper

Compatible:
- jQuery DataTables
- Server Side Processing

Features

✓ Paging
✓ Search
✓ Sorting
✓ Dynamic Filters
✓ Type Conversion
✓ JSON Response
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Request


class DataTable:

    RESERVED = {
        "draw",
        "start",
        "length",
        "search",
        "search[value]",
        "order[0][column]",
        "order[0][dir]",
    }

    def __init__(self, request: Request):

        self.request = request
        self.params = request.query_params

    # --------------------------------------------------
    # BASIC
    # --------------------------------------------------

    @property
    def draw(self) -> int:
        return int(self.params.get("draw", 1))

    @property
    def start(self) -> int:
        return int(self.params.get("start", 0))

    @property
    def length(self) -> int:
        return int(self.params.get("length", 10))

    @property
    def limit(self) -> int:
        return self.length

    @property
    def offset(self) -> int:
        return self.start

    @property
    def page(self) -> int:

        if self.length == 0:
            return 1

        return (self.start // self.length) + 1

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    @property
    def search(self) -> str:

        value = (
            self.params.get("search")
            or self.params.get("search[value]")
            or ""
        )

        return value.strip()

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    @property
    def filters(self) -> dict[str, Any]:

        result = {}

        for key, value in self.params.items():

            if key in self.RESERVED:
                continue

            if key.startswith("columns["):
                continue

            result[key] = value

        return result

    def has_filter(self, key: str) -> bool:
        return key in self.filters

    def get(self, key: str, default=None):
        return self.filters.get(key, default)

    def get_int(self, key: str, default=None):

        value = self.get(key)

        if value in ("", None):
            return default

        try:
            return int(value)
        except Exception:
            return default

    def get_float(self, key: str, default=None):

        value = self.get(key)

        if value in ("", None):
            return default

        try:
            return float(value)
        except Exception:
            return default

    def get_bool(self, key: str, default=None):

        value = self.get(key)

        if value is None:
            return default

        value = value.lower()

        if value in ("1", "true", "yes", "on"):
            return True

        if value in ("0", "false", "no", "off"):
            return False

        return default

    def get_date(self, key: str, fmt="%Y-%m-%d"):

        value = self.get(key)

        if not value:
            return None

        try:
            return datetime.strptime(value, fmt)
        except Exception:
            return None

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------

    @property
    def sort_direction(self):

        direction = self.params.get(
            "order[0][dir]",
            "desc",
        ).lower()

        if direction not in ("asc", "desc"):
            return "desc"

        return direction

    def sort_column(

        self,
        mapping: list[str | None],
        default="created_at",

    ):

        try:

            index = int(
                self.params.get(
                    "order[0][column]",
                    0,
                )
            )

        except Exception:
            return default

        if index >= len(mapping):
            return default

        column = mapping[index]

        if column is None:
            return default

        return column

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    def response(

        self,
        *,
        data,
        total,
        filtered,

    ):

        return {
            "draw": self.draw,
            "recordsTotal": total,
            "recordsFiltered": filtered,
            "data": data,
        }

    def response_empty(self):

        return self.response(
            data=[],
            total=0,
            filtered=0,
        )

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    def to_dict(self):

        return {
            "draw": self.draw,
            "page": self.page,
            "start": self.start,
            "length": self.length,
            "search": self.search,
            "sort": {
                "direction": self.sort_direction,
            },
            "filters": self.filters,
        }