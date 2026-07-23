"""
Channel Mapper - Complete Implementation

Mapper untuk konversi antara:
- Database models (dict dari repository)
- Domain models (DTOs / Data Transfer Objects)
- Request/Response objects untuk API
- Internal service objects

Menggunakan pattern mapping yang konsisten untuk seluruh aplikasi.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# =====================================================
# DTO / SCHEMA CLASSES
# =====================================================

class ChannelDTO:
    """
    Data Transfer Object untuk Channel.
    Digunakan untuk transfer data antar layer.
    """
    
    def __init__(
        self,
        id: int,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        total_artists: int = 0,
        total_songs: int = 0,
        uploaded_songs: int = 0,
        pending_songs: int = 0,
        takedown_songs: int = 0,
        first_song_date: Optional[datetime] = None,
        last_song_date: Optional[datetime] = None,
        status_breakdown: Optional[Dict[str, int]] = None,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.vermuk = vermuk
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at
        self.total_artists = total_artists
        self.total_songs = total_songs
        self.uploaded_songs = uploaded_songs
        self.pending_songs = pending_songs
        self.takedown_songs = takedown_songs
        self.first_song_date = first_song_date
        self.last_song_date = last_song_date
        self.status_breakdown = status_breakdown or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'vermuk': self.vermuk,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_artists': self.total_artists,
            'total_songs': self.total_songs,
            'uploaded_songs': self.uploaded_songs,
            'pending_songs': self.pending_songs,
            'takedown_songs': self.takedown_songs,
            'first_song_date': self.first_song_date.isoformat() if self.first_song_date else None,
            'last_song_date': self.last_song_date.isoformat() if self.last_song_date else None,
            'status_breakdown': self.status_breakdown,
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary (hides password)."""
        data = self.to_dict()
        data.pop('password', None)  # Hide password
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChannelDTO':
        """Create DTO from dictionary."""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            email=data.get('email'),
            password=data.get('password'),
            vermuk=data.get('vermuk', False),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            total_artists=data.get('total_artists', 0),
            total_songs=data.get('total_songs', 0),
            uploaded_songs=data.get('uploaded_songs', 0),
            pending_songs=data.get('pending_songs', 0),
            takedown_songs=data.get('takedown_songs', 0),
            first_song_date=data.get('first_song_date'),
            last_song_date=data.get('last_song_date'),
            status_breakdown=data.get('status_breakdown'),
        )
    
    def __repr__(self) -> str:
        return f"<ChannelDTO id={self.id} name='{self.name}'>"


class ChannelCreateDTO:
    """DTO untuk create channel."""
    
    def __init__(
        self,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
    ):
        self.name = name
        self.email = email
        self.password = password
        self.vermuk = vermuk
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'vermuk': self.vermuk,
            'notes': self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChannelCreateDTO':
        return cls(
            name=data.get('name', ''),
            email=data.get('email'),
            password=data.get('password'),
            vermuk=data.get('vermuk', False),
            notes=data.get('notes'),
        )


class ChannelUpdateDTO:
    """DTO untuk update channel."""
    
    def __init__(
        self,
        id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: Optional[bool] = None,
        notes: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.vermuk = vermuk
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.name is not None:
            data['name'] = self.name
        if self.email is not None:
            data['email'] = self.email
        if self.password is not None:
            data['password'] = self.password
        if self.vermuk is not None:
            data['vermuk'] = self.vermuk
        if self.notes is not None:
            data['notes'] = self.notes
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChannelUpdateDTO':
        return cls(
            id=data.get('id', 0),
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            vermuk=data.get('vermuk'),
            notes=data.get('notes'),
        )


class ChannelFilterDTO:
    """DTO untuk filter channel."""
    
    def __init__(
        self,
        keyword: Optional[str] = None,
        vermuk: Optional[bool] = None,
        email: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
        min_artists: Optional[int] = None,
        max_artists: Optional[int] = None,
        min_songs: Optional[int] = None,
        max_songs: Optional[int] = None,
        order_by: str = 'created_at',
        order_dir: str = 'desc',
        start: int = 0,
        length: int = 20,
    ):
        self.keyword = keyword
        self.vermuk = vermuk
        self.email = email
        self.date_from = date_from
        self.date_to = date_to
        self.has_artists = has_artists
        self.has_songs = has_songs
        self.min_artists = min_artists
        self.max_artists = max_artists
        self.min_songs = min_songs
        self.max_songs = max_songs
        self.order_by = order_by
        self.order_dir = order_dir
        self.start = start
        self.length = min(length, 1000)  # Max limit
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'keyword': self.keyword,
            'vermuk': self.vermuk,
            'email': self.email,
            'date_from': self.date_from.isoformat() if self.date_from else None,
            'date_to': self.date_to.isoformat() if self.date_to else None,
            'has_artists': self.has_artists,
            'has_songs': self.has_songs,
            'min_artists': self.min_artists,
            'max_artists': self.max_artists,
            'min_songs': self.min_songs,
            'max_songs': self.max_songs,
            'order_by': self.order_by,
            'order_dir': self.order_dir,
            'start': self.start,
            'length': self.length,
        }


class ChannelStatsDTO:
    """DTO untuk statistics channel."""
    
    def __init__(
        self,
        total_channels: int = 0,
        total_vermuk: int = 0,
        total_normal: int = 0,
        total_artists: int = 0,
        total_songs: int = 0,
        uploaded_songs: int = 0,
        pending_songs: int = 0,
        takedown_songs: int = 0,
        channels_with_artists: int = 0,
        channels_with_songs: int = 0,
        artists_with_songs: int = 0,
        avg_artists_per_channel: float = 0.0,
        avg_songs_per_channel: float = 0.0,
        avg_songs_per_artist: float = 0.0,
        utilization_rate: float = 0.0,
        status_breakdown: Optional[Dict[str, int]] = None,
        oldest_channel: Optional[datetime] = None,
        newest_channel: Optional[datetime] = None,
        oldest_song: Optional[datetime] = None,
        newest_song: Optional[datetime] = None,
    ):
        self.total_channels = total_channels
        self.total_vermuk = total_vermuk
        self.total_normal = total_normal
        self.total_artists = total_artists
        self.total_songs = total_songs
        self.uploaded_songs = uploaded_songs
        self.pending_songs = pending_songs
        self.takedown_songs = takedown_songs
        self.channels_with_artists = channels_with_artists
        self.channels_with_songs = channels_with_songs
        self.artists_with_songs = artists_with_songs
        self.avg_artists_per_channel = avg_artists_per_channel
        self.avg_songs_per_channel = avg_songs_per_channel
        self.avg_songs_per_artist = avg_songs_per_artist
        self.utilization_rate = utilization_rate
        self.status_breakdown = status_breakdown or {}
        self.oldest_channel = oldest_channel
        self.newest_channel = newest_channel
        self.oldest_song = oldest_song
        self.newest_song = newest_song
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_channels': self.total_channels,
            'total_vermuk': self.total_vermuk,
            'total_normal': self.total_normal,
            'total_artists': self.total_artists,
            'total_songs': self.total_songs,
            'uploaded_songs': self.uploaded_songs,
            'pending_songs': self.pending_songs,
            'takedown_songs': self.takedown_songs,
            'channels_with_artists': self.channels_with_artists,
            'channels_with_songs': self.channels_with_songs,
            'artists_with_songs': self.artists_with_songs,
            'avg_artists_per_channel': self.avg_artists_per_channel,
            'avg_songs_per_channel': self.avg_songs_per_channel,
            'avg_songs_per_artist': self.avg_songs_per_artist,
            'utilization_rate': self.utilization_rate,
            'status_breakdown': self.status_breakdown,
            'oldest_channel': self.oldest_channel.isoformat() if self.oldest_channel else None,
            'newest_channel': self.newest_channel.isoformat() if self.newest_channel else None,
            'oldest_song': self.oldest_song.isoformat() if self.oldest_song else None,
            'newest_song': self.newest_song.isoformat() if self.newest_song else None,
        }


class ChannelActivityDTO:
    """DTO untuk activity score."""
    
    def __init__(
        self,
        channel_id: int,
        channel_name: str,
        total_songs: int,
        total_artists: int,
        recent_songs: int,
        recency_score: float,
        consistency_score: float,
        engagement_score: float,
        growth_score: float,
        overall_score: float,
        level: str,
        last_activity: Optional[datetime] = None,
        avg_songs_per_month: float = 0.0,
        upload_rate: float = 0.0,
    ):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.total_songs = total_songs
        self.total_artists = total_artists
        self.recent_songs = recent_songs
        self.recency_score = recency_score
        self.consistency_score = consistency_score
        self.engagement_score = engagement_score
        self.growth_score = growth_score
        self.overall_score = overall_score
        self.level = level
        self.last_activity = last_activity
        self.avg_songs_per_month = avg_songs_per_month
        self.upload_rate = upload_rate
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'total_songs': self.total_songs,
            'total_artists': self.total_artists,
            'recent_songs': self.recent_songs,
            'recency_score': self.recency_score,
            'consistency_score': self.consistency_score,
            'engagement_score': self.engagement_score,
            'growth_score': self.growth_score,
            'overall_score': self.overall_score,
            'level': self.level,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'avg_songs_per_month': self.avg_songs_per_month,
            'upload_rate': self.upload_rate,
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format."""
        return self.to_dict()


class ChannelListDTO:
    """DTO untuk list channel dengan pagination."""
    
    def __init__(
        self,
        data: List[ChannelDTO],
        total: int,
        start: int = 0,
        length: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ):
        self.data = data
        self.total = total
        self.start = start
        self.length = length
        self.filters = filters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'data': [item.to_json() for item in self.data],
            'meta': {
                'total': self.total,
                'start': self.start,
                'length': self.length,
                'page': (self.start // self.length) + 1 if self.length > 0 else 1,
                'total_pages': (self.total + self.length - 1) // self.length if self.length > 0 else 0,
                'filters': self.filters,
            }
        }


# =====================================================
# MAPPER CLASS
# =====================================================

class ChannelMapper:
    """
    Mapper untuk konversi antara berbagai representasi Channel.
    """
    
    # =====================================================
    # DATABASE TO DTO
    # =====================================================
    
    @staticmethod
    def from_db_to_dto(db_data: Dict[str, Any]) -> ChannelDTO:
        """
        Convert database result to ChannelDTO.
        
        Args:
            db_data: Dictionary from database (repository result)
            
        Returns:
            ChannelDTO object
        """
        return ChannelDTO(
            id=db_data.get('id', 0),
            name=db_data.get('name', ''),
            email=db_data.get('email'),
            password=db_data.get('password'),
            vermuk=db_data.get('vermuk', False),
            notes=db_data.get('notes'),
            created_at=db_data.get('created_at'),
            updated_at=db_data.get('updated_at'),
            total_artists=db_data.get('total_artists', 0),
            total_songs=db_data.get('total_songs', 0),
            uploaded_songs=db_data.get('uploaded_songs', 0),
            pending_songs=db_data.get('pending_songs', 0),
            takedown_songs=db_data.get('takedown_songs', 0),
            first_song_date=db_data.get('first_song_date'),
            last_song_date=db_data.get('last_song_date'),
            status_breakdown=db_data.get('status_breakdown'),
        )
    
    @staticmethod
    def from_db_list_to_dto_list(
        db_data_list: List[Dict[str, Any]]
    ) -> List[ChannelDTO]:
        """
        Convert list of database results to list of ChannelDTO.
        
        Args:
            db_data_list: List of dictionaries from database
            
        Returns:
            List of ChannelDTO objects
        """
        return [
            ChannelMapper.from_db_to_dto(item)
            for item in db_data_list
        ]
    
    # =====================================================
    # STATS TO DTO
    # =====================================================
    
    @staticmethod
    def from_stats_to_dto(stats_data: Dict[str, Any]) -> ChannelStatsDTO:
        """
        Convert statistics data to ChannelStatsDTO.
        
        Args:
            stats_data: Dictionary from statistics repository
            
        Returns:
            ChannelStatsDTO object
        """
        return ChannelStatsDTO(
            total_channels=stats_data.get('total_channels', 0),
            total_vermuk=stats_data.get('total_vermuk', 0),
            total_normal=stats_data.get('total_normal', 0),
            total_artists=stats_data.get('total_artists', 0),
            total_songs=stats_data.get('total_songs', 0),
            uploaded_songs=stats_data.get('uploaded_songs', 0),
            pending_songs=stats_data.get('pending_songs', 0),
            takedown_songs=stats_data.get('takedown_songs', 0),
            channels_with_artists=stats_data.get('channels_with_artists', 0),
            channels_with_songs=stats_data.get('channels_with_songs', 0),
            artists_with_songs=stats_data.get('artists_with_songs', 0),
            avg_artists_per_channel=float(stats_data.get('avg_artists_per_channel', 0)),
            avg_songs_per_channel=float(stats_data.get('avg_songs_per_channel', 0)),
            avg_songs_per_artist=float(stats_data.get('avg_songs_per_artist', 0)),
            utilization_rate=float(stats_data.get('utilization_rate', 0)),
            status_breakdown=stats_data.get('status_breakdown', {}),
            oldest_channel=stats_data.get('oldest_channel'),
            newest_channel=stats_data.get('newest_channel'),
            oldest_song=stats_data.get('oldest_song'),
            newest_song=stats_data.get('newest_song'),
        )
    
    # =====================================================
    # ACTIVITY TO DTO
    # =====================================================
    
    @staticmethod
    def from_activity_to_dto(
        activity_data: Dict[str, Any],
        channel_name: str = ''
    ) -> ChannelActivityDTO:
        """
        Convert activity data to ChannelActivityDTO.
        
        Args:
            activity_data: Dictionary from activity calculation
            channel_name: Channel name (optional)
            
        Returns:
            ChannelActivityDTO object
        """
        return ChannelActivityDTO(
            channel_id=activity_data.get("channel_id", 0),
            channel_name=channel_name or activity_data.get("channel_name", ""),
            total_songs=activity_data.get("total_songs") or 0,
            total_artists=activity_data.get("total_artists") or 0,
            recent_songs=activity_data.get("recent_songs") or 0,

            recency_score=ChannelMapper._to_float(activity_data.get("recency_score")),
            consistency_score=ChannelMapper._to_float(activity_data.get("consistency_score")),
            engagement_score=ChannelMapper._to_float(activity_data.get("engagement_score")),
            growth_score=ChannelMapper._to_float(activity_data.get("growth_score")),
            overall_score=ChannelMapper._to_float(activity_data.get("overall_score")),


            level=activity_data.get("level") or "Inactive",
            last_activity=activity_data.get("last_activity"),

            avg_songs_per_month=ChannelMapper._to_float(activity_data.get("avg_songs_per_month")),
            upload_rate=ChannelMapper._to_float(activity_data.get("upload_rate")),
        )

    @staticmethod
    def _to_float(value: Any) -> float:
        if value is None:
            return 0.0
        return float(value)
    
    # =====================================================
    # REQUEST TO DTO
    # =====================================================
    
    @staticmethod
    def from_create_request(data: Dict[str, Any]) -> ChannelCreateDTO:
        """
        Convert API request to ChannelCreateDTO.
        
        Args:
            data: Dictionary from API request
            
        Returns:
            ChannelCreateDTO object
        """
        return ChannelCreateDTO(
            name=data.get('name', '').strip(),
            email=data.get('email'),
            password=data.get('password'),
            vermuk=data.get('vermuk', False),
            notes=data.get('notes'),
        )
    
    @staticmethod
    def from_update_request(data: Dict[str, Any]) -> ChannelUpdateDTO:
        """
        Convert API request to ChannelUpdateDTO.
        
        Args:
            data: Dictionary from API request
            
        Returns:
            ChannelUpdateDTO object
        """
        return ChannelUpdateDTO(
            id=data.get('id', 0),
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            vermuk=data.get('vermuk'),
            notes=data.get('notes'),
        )
    
    @staticmethod
    def from_filter_request(data: Dict[str, Any]) -> ChannelFilterDTO:
        """
        Convert API request to ChannelFilterDTO.
        
        Args:
            data: Dictionary from API request
            
        Returns:
            ChannelFilterDTO object
        """
        return ChannelFilterDTO(
            keyword=data.get('keyword'),
            vermuk=data.get('vermuk'),
            email=data.get('email'),
            date_from=data.get('date_from'),
            date_to=data.get('date_to'),
            has_artists=data.get('has_artists'),
            has_songs=data.get('has_songs'),
            min_artists=data.get('min_artists'),
            max_artists=data.get('max_artists'),
            min_songs=data.get('min_songs'),
            max_songs=data.get('max_songs'),
            order_by=data.get('order_by', 'created_at'),
            order_dir=data.get('order_dir', 'desc'),
            start=data.get('start', 0),
            length=data.get('length', 20),
        )
    
    # =====================================================
    # DTO TO DATABASE
    # =====================================================
    
    @staticmethod
    def dto_to_create_dict(dto: ChannelCreateDTO) -> Dict[str, Any]:
        """
        Convert ChannelCreateDTO to dictionary for repository.
        
        Args:
            dto: ChannelCreateDTO object
            
        Returns:
            Dictionary for repository create method
        """
        return dto.to_dict()
    
    @staticmethod
    def dto_to_update_dict(dto: ChannelUpdateDTO) -> Dict[str, Any]:
        """
        Convert ChannelUpdateDTO to dictionary for repository.
        
        Args:
            dto: ChannelUpdateDTO object
            
        Returns:
            Dictionary for repository update method
        """
        return dto.to_dict()
    
    @staticmethod
    def dto_to_filter_dict(dto: ChannelFilterDTO) -> Dict[str, Any]:
        """
        Convert ChannelFilterDTO to dictionary for repository.
        
        Args:
            dto: ChannelFilterDTO object
            
        Returns:
            Dictionary for repository filter method
        """
        return dto.to_dict()
    
    # =====================================================
    # TRANSFORM / ENRICH
    # =====================================================
    
    @staticmethod
    def enrich_with_stats(
        channel_dto: ChannelDTO,
        stats_data: Dict[str, Any]
    ) -> ChannelDTO:
        """
        Enrich channel DTO with additional statistics.
        
        Args:
            channel_dto: ChannelDTO object
            stats_data: Statistics data
            
        Returns:
            Enriched ChannelDTO object
        """
        if stats_data:
            channel_dto.total_artists = stats_data.get('total_artists', 0)
            channel_dto.total_songs = stats_data.get('total_songs', 0)
            channel_dto.uploaded_songs = stats_data.get('uploaded_songs', 0)
            channel_dto.pending_songs = stats_data.get('pending_songs', 0)
            channel_dto.takedown_songs = stats_data.get('takedown_songs', 0)
            channel_dto.first_song_date = stats_data.get('first_song_date')
            channel_dto.last_song_date = stats_data.get('last_song_date')
            channel_dto.status_breakdown = stats_data.get('status_breakdown', {})
        
        return channel_dto
    
    @staticmethod
    def enrich_with_activity(
        channel_dto: ChannelDTO,
        activity_data: Dict[str, Any]
    ) -> ChannelDTO:
        """
        Enrich channel DTO with activity data.
        
        Args:
            channel_dto: ChannelDTO object
            activity_data: Activity data
            
        Returns:
            Enriched ChannelDTO object
        """
        if activity_data:
            channel_dto.activity_level = activity_data.get('level')
            channel_dto.activity_score = activity_data.get('overall_score')
            channel_dto.recent_songs = activity_data.get('recent_songs', 0)
        
        return channel_dto
    
    # =====================================================
    # BULK RESULTS
    # =====================================================
    
    @staticmethod
    def format_bulk_result(
        result: Dict[str, Any],
        action: str = 'processed'
    ) -> Dict[str, Any]:
        """
        Format bulk operation result.
        
        Args:
            result: Raw bulk result from repository
            action: Action name (deleted, updated, inserted)
            
        Returns:
            Formatted result
        """
        return {
            'action': action,
            'success': result.get('success', True),
            'count': result.get(f'{action}_count', result.get('count', 0)),
            'details': {
                'successful': result.get(f'{action}_ids', []),
                'successful_count': result.get(f'{action}_count', 0),
                'failed': result.get('failed', []),
                'failed_count': len(result.get('failed', [])),
                'skipped': result.get('skipped', []),
                'skipped_count': len(result.get('skipped', [])),
                'not_found': result.get('not_found', []),
                'not_found_count': len(result.get('not_found', [])),
            },
            'total_requested': result.get('total_requested', 0),
            'timestamp': datetime.now().isoformat(),
        }
    
    # =====================================================
    # RESPONSE FORMATS
    # =====================================================
    
    @staticmethod
    def to_response(
        data: Union[ChannelDTO, List[ChannelDTO], Dict[str, Any]],
        status_code: int = 200,
        message: str = "Success",
    ) -> Dict[str, Any]:
        response = {
            "success": status_code < 400,
            "status_code": status_code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        if isinstance(data, ChannelDTO):
            response["data"] = data.to_json()

        elif isinstance(data, list) and all(isinstance(x, ChannelDTO) for x in data):
            response["data"] = [x.to_json() for x in data]
            response["count"] = len(data)

        elif isinstance(data, ChannelListDTO):
            response["data"] = data.to_dict()

        elif isinstance(data, dict):
            response["data"] = data

        else:
            response["data"] = data

        return response
    
    @staticmethod
    def to_error_response(
        error: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format error response.
        
        Args:
            error: Error message
            status_code: HTTP status code
            details: Additional error details
            
        Returns:
            Formatted error response
        """
        response = {
            'success': False,
            'status_code': status_code,
            'error': error,
            'timestamp': datetime.now().isoformat(),
        }
        
        if details:
            response['details'] = details
        
        return response