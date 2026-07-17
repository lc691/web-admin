from __future__ import annotations

from datetime import date, datetime
from typing import TypedDict


class UsageRow(TypedDict):
    usage_id: int

    song_id: int
    title: str
    status: str
    status_text: str
    release_date: date | None

    artist_id: int
    artist: str

    channel_id: int
    channel: str

    day: int
    mode: str

    used_at: datetime


class UsageStatistics(TypedDict):
    total_usage: int

    total_channels: int
    total_artists: int

    live_songs: int
    approved_songs: int
    review_songs: int
    takedown_songs: int
    topic_songs: int

    first_used: datetime | None
    last_used: datetime | None