"""
Channel Presenter
"""

from typing import Optional, List, Dict, Any


class ChannelPresenter:
    @staticmethod
    def list(
        *,
        channels: List[Dict[str, Any]],
        years: Optional[List[Dict[str, Any]]] = None,
        keyword: Optional[str] = None,
        year: Optional[int] = None,
        has_youtube: Optional[bool] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
        total: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        """Prepare context for channel list page."""
        
        # Calculate totals
        total_artists = sum(
            channel.get("total_artists", 0) or 0
            for channel in channels
        )

        total_songs = sum(
            channel.get("total_songs", 0) or 0
            for channel in channels
        )

        total_live_songs = sum(
            channel.get("live_songs", 0) or 0
            for channel in channels
        )

        # Get channel IDs for display
        channel_ids = [channel.get("id") for channel in channels]

        return {
            "channels": channels,
            "channel_ids": channel_ids,
            "years": years or [],
            
            "total_channels": total or len(channels),
            "total_artists": total_artists,
            "total_songs": total_songs,
            "total_live_songs": total_live_songs,
            
            "filters": {
                "keyword": keyword,
                "year": year,
                "has_youtube": has_youtube,
                "has_artists": has_artists,
                "has_songs": has_songs,
            },
            
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total or len(channels),
                "total_pages": (total or len(channels) + per_page - 1) // per_page if total else 1,
            }
        }

    @staticmethod
    def form(
        *,
        channel: Optional[Dict[str, Any]] = None,
        errors: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Prepare context for channel form page."""
        return {
            "channel": channel,
            "errors": errors or {},
            "is_edit": channel is not None,
        }

    @staticmethod
    def detail(
        *,
        channel: Dict[str, Any],
        artists: List[Dict[str, Any]],
        songs: List[Dict[str, Any]],
        summary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Prepare context for channel detail page."""
        
        # Calculate summary statistics
        if summary:
            total_artists = summary.get("total_artists", 0)
            total_songs = summary.get("total_songs", 0)
            live_songs = summary.get("live_songs", 0)
        else:
            total_artists = len(artists)
            total_songs = len(songs)
            live_songs = len([s for s in songs if s.get("status") == "Live"])

        # Group songs by status
        songs_by_status = {}
        for song in songs:
            status = song.get("status", "Unknown")
            if status not in songs_by_status:
                songs_by_status[status] = []
            songs_by_status[status].append(song)

        return {
            "channel": channel,
            "artists": artists,
            "songs": songs,
            "songs_by_status": songs_by_status,
            "summary": summary or {
                "total_artists": total_artists,
                "total_songs": total_songs,
                "live_songs": live_songs,
            },
            "total_artists": total_artists,
            "total_songs": total_songs,
            "live_songs": live_songs,
        }

    @staticmethod
    def api(
        data: Any,
        success: bool = True,
        message: Optional[str] = None,
        total: Optional[int] = None,
        **extra: Any,
    ) -> Dict[str, Any]:
        """Prepare API response."""
        response = {
            "success": success,
            "data": data,
        }

        if message:
            response["message"] = message

        if total is not None:
            response["total"] = total

        response.update(extra)

        return response