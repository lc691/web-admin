"""
Channel Service
"""

from typing import Optional, List, Dict, Any
from fastapi import HTTPException

from app.music.repositories.channels.repository import ChannelRepository
from app.music.repositories.channels.statistics import (
    ChannelStatisticsRepository,
)
from app.music.repositories.channels.search import ChannelSearchRepository
from app.music.repositories.channels.filter import (
    ChannelFilterRepository,
)


class ChannelService:
    def __init__(self, cursor):
        self.cursor = cursor

        self.repository = ChannelRepository(cursor)
        self.statistics = ChannelStatisticsRepository(cursor)
        self.search_repository = ChannelSearchRepository(cursor)
        self.filter_repository = ChannelFilterRepository(cursor)

    # =====================================================
    # LIST
    # =====================================================

    def get_all(
        self,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self.repository.find_all(search, limit, offset)

    # =====================================================
    # DETAIL
    # =====================================================

    def get(self, channel_id: int) -> Dict[str, Any]:
        channel = self.repository.find_by_id(channel_id)

        if not channel:
            raise HTTPException(
                status_code=404,
                detail="Channel tidak ditemukan.",
            )

        return channel

    def get_detail(self, channel_id: int) -> Dict[str, Any]:
        channel = self.get(channel_id)
        artists = self.repository.get_artists(channel_id)
        songs = self.repository.get_recent_songs(channel_id)
        summary = self.statistics.summary(channel_id)

        return {
            "channel": channel,
            "artists": artists,
            "songs": songs,
            "summary": summary,
        }

    # =====================================================
    # SEARCH & FILTER
    # =====================================================

    def search(
        self,
        keyword: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        return self.search_repository.search(keyword, limit)

    def autocomplete(
        self,
        keyword: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        return self.search_repository.autocomplete(keyword, limit)

    def years(self) -> List[Dict[str, Any]]:
        return self.filter_repository.years()

    def filter(
        self,
        keyword: Optional[str] = None,
        year: Optional[int] = None,
        has_youtube: Optional[bool] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self.filter_repository.apply(
            keyword=keyword,
            year=year,
            has_youtube=has_youtube,
            has_artists=has_artists,
            has_songs=has_songs,
            limit=limit,
            offset=offset,
        )

    def count_filtered(
        self,
        keyword: Optional[str] = None,
        year: Optional[int] = None,
        has_youtube: Optional[bool] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
    ) -> int:
        return self.filter_repository.count_filtered(
            keyword=keyword,
            year=year,
            has_youtube=has_youtube,
            has_artists=has_artists,
            has_songs=has_songs,
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    def overview(self) -> Dict[str, Any]:
        return self.statistics.overview()

    def summary(self, channel_id: int) -> Dict[str, Any]:
        return self.statistics.summary(channel_id)

    def status_distribution(self, channel_id: int) -> List[Dict[str, Any]]:
        return self.statistics.status_distribution(channel_id)

    def top_channels(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.statistics.top_channels(limit)