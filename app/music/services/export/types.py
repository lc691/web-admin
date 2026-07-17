from typing import Literal, TypedDict

ExportMode = Literal[
    "normal",
    "clean",
    "blacklist",
]


class SongRow(TypedDict):
    id: int
    title: str
    artist: str
    channel_id: int
    channel: str


class ExportInformation(TypedDict):
    remaining: int
    already_exported: bool
    unique_songs: int
    total_available: int
    day: int
    mode: ExportMode 

class ExportBatch(TypedDict):
    id: int
    day: int
    duplicate: int
    target: int
    channel_limit: int
    excluded_channels: list[int]
    mode: ExportMode

class ExportBatchItem(TypedDict):
    id: int
    batch_id: int
    song_id: int
    order_index: int


__all__ = [
    "ExportBatch",
    "ExportBatchItem",
    "ExportInformation",
    "ExportMode",
    "SongRow",
]