"""
Artist Mapper - Complete Implementation

Mapper untuk konversi antara:
- Database models (dict dari repository)
- Domain models (DTOs / Data Transfer Objects)
- Request/Response objects untuk API
- Internal service objects
- DataTable responses
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# =====================================================
# DTO / SCHEMA CLASSES
# =====================================================

class ArtistDTO:
    """
    Data Transfer Object untuk Artist.
    Digunakan untuk transfer data antar layer.
    """

    def __init__(
        self,
        id: int,
        name: str,
        channel_id: int,
        channel_name: Optional[str] = None,
        song_count: int = 0,
        uploaded_songs: int = 0,
        pending_songs: int = 0,
        takedown_songs: int = 0,
        first_song_date: Optional[datetime] = None,
        last_song_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.song_count = song_count
        self.uploaded_songs = uploaded_songs
        self.pending_songs = pending_songs
        self.takedown_songs = takedown_songs
        self.first_song_date = first_song_date
        self.last_song_date = last_song_date
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'song_count': self.song_count,
            'uploaded_songs': self.uploaded_songs,
            'pending_songs': self.pending_songs,
            'takedown_songs': self.takedown_songs,
            'first_song_date': self.first_song_date.isoformat() if self.first_song_date else None,
            'last_song_date': self.last_song_date.isoformat() if self.last_song_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtistDTO':
        """Create DTO from dictionary."""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            channel_id=data.get('channel_id', 0),
            channel_name=data.get('channel_name'),
            song_count=data.get('song_count', 0),
            uploaded_songs=data.get('uploaded_songs', 0),
            pending_songs=data.get('pending_songs', 0),
            takedown_songs=data.get('takedown_songs', 0),
            first_song_date=data.get('first_song_date'),
            last_song_date=data.get('last_song_date'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )

    def __repr__(self) -> str:
        return f"<ArtistDTO id={self.id} name='{self.name}' channel_id={self.channel_id}>"


class ArtistCreateDTO:
    """DTO untuk create artist."""

    def __init__(
        self,
        channel_id: int,
        name: str,
    ):
        self.channel_id = channel_id
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            'channel_id': self.channel_id,
            'name': self.name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtistCreateDTO':
        return cls(
            channel_id=data.get('channel_id', 0),
            name=data.get('name', ''),
        )


class ArtistUpdateDTO:
    """DTO untuk update artist."""

    def __init__(
        self,
        id: int,
        channel_id: Optional[int] = None,
        name: Optional[str] = None,
    ):
        self.id = id
        self.channel_id = channel_id
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.channel_id is not None:
            data['channel_id'] = self.channel_id
        if self.name is not None:
            data['name'] = self.name
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtistUpdateDTO':
        return cls(
            id=data.get('id', 0),
            channel_id=data.get('channel_id'),
            name=data.get('name'),
        )


class ArtistStatsDTO:
    """DTO untuk statistics artist."""

    def __init__(
        self,
        total_artists: int = 0,
        total_songs: int = 0,
        active_channels: int = 0,
        artists_with_songs: int = 0,
        artists_without_songs: int = 0,
        avg_songs_per_artist: float = 0.0,
    ):
        self.total_artists = total_artists
        self.total_songs = total_songs
        self.active_channels = active_channels
        self.artists_with_songs = artists_with_songs
        self.artists_without_songs = artists_without_songs
        self.avg_songs_per_artist = avg_songs_per_artist

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_artists': self.total_artists,
            'total_songs': self.total_songs,
            'active_channels': self.active_channels,
            'artists_with_songs': self.artists_with_songs,
            'artists_without_songs': self.artists_without_songs,
            'avg_songs_per_artist': self.avg_songs_per_artist,
        }


# =====================================================
# MAPPER CLASS
# =====================================================

class ArtistMapper:
    """
    Mapper Artist untuk konversi data.
    """

    # =====================================================
    # DATATABLE
    # =====================================================

    @staticmethod
    def to_datatable(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format Artist untuk DataTables.
        """

        created_at = row.get("created_at")
        updated_at = row.get("updated_at")
        last_song_date = row.get("last_song_date")

        return {
            "id": row.get("id"),
            "channel_id": row.get("channel_id"),

            "channel_name": row.get("channel_name", "-"),
            "channel_vermuk": row.get("channel_vermuk", False),

            "name": row.get("name"),

            "song_count": row.get("song_count", 0),
            "uploaded_songs": row.get("uploaded_songs", 0),
            "pending_songs": row.get("pending_songs", 0),
            "takedown_songs": row.get("takedown_songs", 0),

            "song_status": row.get("song_status"),

            "last_song_date": (
                last_song_date.strftime("%Y-%m-%d %H:%M")
                if last_song_date
                else None
            ),

            "created_at": (
                created_at.strftime("%Y-%m-%d %H:%M")
                if created_at
                else None
            ),

            "updated_at": (
                updated_at.strftime("%Y-%m-%d %H:%M")
                if updated_at
                else None
            ),

            "actions": {
                "edit": f"/artists/{row.get('id')}/edit",
                "detail": f"/artists/{row.get('id')}/detail",
                "delete": f"/artists/{row.get('id')}/delete",
            },
        }

    # =====================================================
    # DETAIL
    # =====================================================

    @staticmethod
    def to_detail(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format untuk halaman detail artist.
        
        Args:
            row: Database row
            
        Returns:
            Formatted detail data
        """
        created_at = row.get("created_at")
        updated_at = row.get("updated_at")
        first_song = row.get("first_song_date")
        last_song = row.get("last_song_date")

        return {
            "id": row.get("id"),
            "channel_id": row.get("channel_id"),
            "channel_name": row.get("channel_name"),
            "channel_vermuk": row.get("channel_vermuk", False),
            "name": row.get("name"),
            "song_count": row.get("song_count", 0),
            "uploaded_songs": row.get("uploaded_songs", 0),
            "pending_songs": row.get("pending_songs", 0),
            "takedown_songs": row.get("takedown_songs", 0),
            "first_song_date": (
                first_song.strftime("%Y-%m-%d")
                if first_song
                else None
            ),
            "last_song_date": (
                last_song.strftime("%Y-%m-%d")
                if last_song
                else None
            ),
            "created_at": (
                created_at.strftime("%Y-%m-%d %H:%M")
                if created_at
                else None
            ),
            "updated_at": (
                updated_at.strftime("%Y-%m-%d %H:%M")
                if updated_at
                else None
            ),
            "upload_rate": row.get("upload_rate", 0),
            "pending_rate": row.get("pending_rate", 0),
            "days_active": row.get("days_active", 0),
            "songs_per_day": row.get("songs_per_day", 0),
        }

    @staticmethod
    def to_detail_with_stats(row: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format detail dengan statistik tambahan.
        
        Args:
            row: Database row
            stats: Additional statistics
            
        Returns:
            Formatted detail with stats
        """
        detail = ArtistMapper.to_detail(row)
        detail.update({
            "total_songs": stats.get("total_songs", 0),
            "status_breakdown": stats.get("status_breakdown", []),
            "upload_rate": stats.get("upload_rate", 0),
            "pending_rate": stats.get("pending_rate", 0),
            "days_active": stats.get("days_active", 0),
            "songs_per_day": stats.get("songs_per_day", 0),
        })
        return detail

    # =====================================================
    # FORM
    # =====================================================

    @staticmethod
    def to_form(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format untuk form edit artist.
        
        Args:
            row: Database row
            
        Returns:
            Formatted form data
        """
        return {
            "id": row.get("id"),
            "channel_id": row.get("channel_id"),
            "name": row.get("name"),
            "channel_name": row.get("channel_name"),
        }

    @staticmethod
    def to_form_with_channels(row: Dict[str, Any], channels: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format untuk form dengan daftar channel.
        
        Args:
            row: Database row
            channels: List of channels for dropdown
            
        Returns:
            Formatted form data with channels
        """
        form = ArtistMapper.to_form(row)
        form["channels"] = channels
        return form

    # =====================================================
    # RESPONSE
    # =====================================================

    @staticmethod
    def to_response(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON Response untuk API.
        
        Args:
            row: Database row
            
        Returns:
            Formatted JSON response
        """
        created_at = row.get("created_at")
        updated_at = row.get("updated_at")

        return {
            "id": row.get("id"),
            "channel_id": row.get("channel_id"),
            "channel_name": row.get("channel_name"),
            "name": row.get("name"),
            "song_count": row.get("song_count", 0),
            "uploaded_songs": row.get("uploaded_songs", 0),
            "pending_songs": row.get("pending_songs", 0),
            "takedown_songs": row.get("takedown_songs", 0),
            "created_at": (
                created_at.isoformat() if created_at else None
            ),
            "updated_at": (
                updated_at.isoformat() if updated_at else None
            ),
        }

    @staticmethod
    def to_response_with_stats(row: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON Response dengan statistik tambahan.
        
        Args:
            row: Database row
            stats: Additional statistics
            
        Returns:
            Formatted JSON response with stats
        """
        response = ArtistMapper.to_response(row)
        response.update({
            "stats": {
                "total_songs": stats.get("total_songs", 0),
                "uploaded_songs": stats.get("uploaded_songs", 0),
                "pending_songs": stats.get("pending_songs", 0),
                "takedown_songs": stats.get("takedown_songs", 0),
                "upload_rate": stats.get("upload_rate", 0),
                "pending_rate": stats.get("pending_rate", 0),
                "days_active": stats.get("days_active", 0),
                "songs_per_day": stats.get("songs_per_day", 0),
                "status_breakdown": stats.get("status_breakdown", []),
            }
        })
        return response

    # =====================================================
    # LIST
    # =====================================================

    @classmethod
    def to_list(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mapping list artist.
        
        Args:
            rows: List of database rows
            
        Returns:
            List of formatted artists
        """
        return [cls.to_datatable(row) for row in rows]

    @classmethod
    def to_list_simple(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simple list for dropdowns.
        
        Args:
            rows: List of database rows
            
        Returns:
            List of simple artist data
        """
        return [
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "channel_id": row.get("channel_id"),
                "channel_name": row.get("channel_name"),
            }
            for row in rows
        ]

    @classmethod
    def to_list_with_stats(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        List with statistics.
        
        Args:
            rows: List of database rows with stats
            
        Returns:
            List of formatted artists with stats
        """
        return [
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "channel_id": row.get("channel_id"),
                "channel_name": row.get("channel_name"),
                "song_count": row.get("song_count", 0),
                "uploaded_songs": row.get("uploaded_songs", 0),
                "pending_songs": row.get("pending_songs", 0),
                "created_at": (
                    row.get("created_at").strftime("%Y-%m-%d %H:%M")
                    if row.get("created_at")
                    else None
                ),
                "actions": {
                    "edit": f"/artists/{row.get('id')}/edit",
                    "detail": f"/artists/{row.get('id')}/detail",
                }
            }
            for row in rows
        ]

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def to_statistics(stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapping statistik artist.
        
        Args:
            stats: Statistics data
            
        Returns:
            Formatted statistics
        """
        return {
            "total_artists": stats.get("total_artists", 0),
            "total_songs": stats.get("total_songs", 0),
            "active_channels": stats.get("active_channels", 0),
            "artists_with_songs": stats.get("artists_with_songs", 0),
            "artists_without_songs": stats.get("artists_without_songs", 0),
            "avg_songs_per_artist": float(stats.get("avg_songs_per_artist", 0)),
        }

    @staticmethod
    def to_channel_statistics(stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapping statistik channel.
        
        Args:
            stats: Channel statistics data
            
        Returns:
            Formatted channel statistics
        """
        return {
            "total_artists": stats.get("total_artists", 0),
            "total_songs": stats.get("total_songs", 0),
            "artists_with_songs": stats.get("artists_with_songs", 0),
            "artists_without_songs": stats.get("artists_without_songs", 0),
            "avg_songs_per_artist": float(stats.get("avg_songs_per_artist", 0)),
            "oldest_artist": (
                stats.get("oldest_artist").strftime("%Y-%m-%d")
                if stats.get("oldest_artist")
                else None
            ),
            "newest_artist": (
                stats.get("newest_artist").strftime("%Y-%m-%d")
                if stats.get("newest_artist")
                else None
            ),
        }

    # =====================================================
    # SELECT / DROPDOWN
    # =====================================================

    @staticmethod
    def to_select(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dropdown Artist.
        
        Args:
            rows: List of database rows
            
        Returns:
            List of artist options
        """
        return [
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "channel_id": row.get("channel_id"),
                "channel_name": row.get("channel_name"),
                "song_count": row.get("song_count", 0),
            }
            for row in rows
        ]

    @staticmethod
    def to_select_grouped(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dropdown Artist yang dikelompokkan berdasarkan channel.
        
        Args:
            rows: List of database rows
            
        Returns:
            Grouped artist options
        """
        grouped = {}
        for row in rows:
            channel_id = row.get("channel_id")
            channel_name = row.get("channel_name", "Unknown Channel")
            
            if channel_id not in grouped:
                grouped[channel_id] = {
                    "label": channel_name,
                    "options": []
                }
            
            grouped[channel_id]["options"].append({
                "id": row.get("id"),
                "name": row.get("name"),
                "song_count": row.get("song_count", 0),
            })
        
        return list(grouped.values())

    # =====================================================
    # CHANNELS
    # =====================================================

    @staticmethod
    def channels(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dropdown Channel.
        
        Args:
            rows: List of channel data
            
        Returns:
            List of channel options
        """
        return [
            {
                "id": row.get("id"),
                "name": row.get("name"),
            }
            for row in rows
        ]

    @staticmethod
    def channel(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Single channel data.
        
        Args:
            row: Channel data
            
        Returns:
            Formatted channel data
        """
        if not row:
            return {}
        
        return {
            "id": row.get("id"),
            "name": row.get("name"),
            "email": row.get("email"),
            "vermuk": row.get("vermuk", False),
            "notes": row.get("notes"),
            "created_at": (
                row.get("created_at").strftime("%Y-%m-%d %H:%M")
                if row.get("created_at")
                else None
            ),
            "updated_at": (
                row.get("updated_at").strftime("%Y-%m-%d %H:%M")
                if row.get("updated_at")
                else None
            ),
        }

    # =====================================================
    # BULK RESPONSE
    # =====================================================

    @staticmethod
    def to_bulk_response(
        result: Dict[str, Any],
        action: str = "processed"
    ) -> Dict[str, Any]:
        """
        Format bulk operation result.
        
        Args:
            result: Raw bulk result from repository
            action: Action name (deleted, updated, inserted)
            
        Returns:
            Formatted bulk response
        """
        return {
            "action": action,
            "success": result.get("success", True),
            "count": result.get(f"{action}_count", result.get("count", 0)),
            "details": {
                "successful": result.get(f"{action}_ids", []),
                "successful_count": result.get(f"{action}_count", 0),
                "failed": result.get("failed", []),
                "failed_count": len(result.get("failed", [])),
                "skipped": result.get("skipped", []),
                "skipped_count": len(result.get("skipped", [])),
                "not_found": result.get("not_found", []),
                "not_found_count": len(result.get("not_found", [])),
            },
            "total_requested": result.get("total_requested", 0),
            "timestamp": datetime.now().isoformat(),
        }

    # =====================================================
    # API RESPONSE FORMATS
    # =====================================================

    @staticmethod
    def to_api_response(
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        status_code: int = 200,
        message: str = "Success"
    ) -> Dict[str, Any]:
        """
        Format API response.
        
        Args:
            data: Data to return
            status_code: HTTP status code
            message: Response message
            
        Returns:
            Formatted API response
        """
        response = {
            "success": status_code < 400,
            "status_code": status_code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        
        if isinstance(data, list):
            response["data"] = data
            response["count"] = len(data)
        else:
            response["data"] = data
        
        return response

    @staticmethod
    def to_api_error(
        error: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format API error response.
        
        Args:
            error: Error message
            status_code: HTTP status code
            details: Additional error details
            
        Returns:
            Formatted error response
        """
        response = {
            "success": False,
            "status_code": status_code,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        
        if details:
            response["details"] = details
        
        return response