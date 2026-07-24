"""
Artist Presenter - Complete Implementation

Presenter layer untuk Artist dengan:
- Context generation untuk templates
- Data formatting untuk UI
- Statistics presentation
- Bulk operation responses
- Consistent structure for views
- Breadcrumb navigation
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.music.services.artists.service import ArtistService
from app.music.services.artists.mapper import ArtistMapper
from app.music.services.artists.exceptions import (
    ArtistNotFoundError,
    ChannelNotFoundError,
)

logger = logging.getLogger(__name__)


class ArtistPresenter:
    """
    Presenter Artist untuk semua halaman.
    """

    # =====================================================
    # CONSTANTS
    # =====================================================

    MODULE = "artists"
    ICON = "ti ti-microphone"
    MODULE_NAME = "Artists"
    MODULE_DESCRIPTION = "Kelola artist dan lagu"

    # Status colors for UI
    STATUS_COLORS = {
        'released': 'success',
        'unreleased': 'warning',
        'scheduled': 'info',
        'review': 'primary',
        'approved': 'success',
        'live': 'danger',
        'take_down': 'danger',
        'topic': 'info',
        'draft': 'secondary',
        'no_ads': 'dark',
    }

    # =====================================================
    # BASE CONTEXT
    # =====================================================

    @classmethod
    def base(cls) -> Dict[str, Any]:
        """
        Context dasar semua halaman Artist.
        """
        return {
            "module": cls.MODULE,
            "icon": cls.ICON,
            "module_name": cls.MODULE_NAME,
            "module_description": cls.MODULE_DESCRIPTION,
            "status_colors": cls.STATUS_COLORS,
            "current_year": datetime.now().year,
        }

    @classmethod
    def with_breadcrumb(
        cls,
        context: Dict[str, Any],
        breadcrumb: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Add breadcrumb to context.
        """
        context['breadcrumb'] = breadcrumb
        return context

    # =====================================================
    # INDEX / LIST
    # =====================================================

    @staticmethod
    def list() -> Dict[str, Any]:
        """
        Data halaman artist.
        """
        try:
            channels = ArtistService.get_channels()
            statistics = ArtistService.statistics()

            context = {
                **ArtistPresenter.base(),
                "page": "index",
                "title": "Artists",
                "subtitle": "Kelola daftar artist",
                "channels": channels,
                "statistics": statistics,
                "view": "list",
            }

            # Add breadcrumb
            context = ArtistPresenter.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Artists", "url": "/admin/artists", "active": True},
            ])

            return context

        except Exception as e:
            logger.error(f"Error in list presenter: {e}")
            return {
                **ArtistPresenter.base(),
                "page": "index",
                "title": "Artists",
                "subtitle": "Kelola daftar artist",
                "channels": [],
                "statistics": {},
                "error": str(e),
            }

    # =====================================================
    # DETAIL
    # =====================================================

    @staticmethod
    def detail(
        artist_id: int,
    ) -> Dict[str, Any]:
        """
        Detail artist.
        """
        try:
            artist = ArtistService.get_detail(
                artist_id,
                include_songs=True,
            )

            if not artist:
                raise ArtistNotFoundError(artist_id=artist_id)

            # Get additional statistics
            statistics = {
                "total_songs": ArtistService.total_songs(artist_id),
                "song_status": ArtistService.song_status(artist_id),
            }

            # Get channel info
            channel_info = None
            if artist.get('channel_id'):
                try:
                    from app.music.services.channels.service import ChannelService
                    # Get channel detail (assuming service method exists)
                    pass
                except:
                    pass

            context = {
                **ArtistPresenter.base(),
                "page": "detail",
                "title": artist.get('name', 'Artist Detail'),
                "subtitle": "Informasi lengkap artist",
                "artist": artist,
                "statistics": statistics,
                "channel_info": channel_info,
                "can_edit": True,
                "can_delete": True,
            }

            # Add breadcrumb
            context = ArtistPresenter.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Artists", "url": "/admin/artists"},
                {"label": artist.get('name', 'Detail'), "url": "#", "active": True},
            ])

            return context

        except ArtistNotFoundError:
            logger.error(f"Artist not found: {artist_id}")
            return {
                **ArtistPresenter.base(),
                "page": "error",
                "title": "Artist Tidak Ditemukan",
                "subtitle": "Artist yang Anda cari tidak ditemukan",
                "error": f"Artist dengan ID {artist_id} tidak ditemukan",
            }
        except Exception as e:
            logger.error(f"Error in detail presenter: {e}")
            return {
                **ArtistPresenter.base(),
                "page": "error",
                "title": "Error",
                "subtitle": "Terjadi kesalahan",
                "error": str(e),
            }

    # =====================================================
    # FORM CREATE
    # =====================================================

    @staticmethod
    def create() -> Dict[str, Any]:
        """
        Data form create artist.
        """
        try:
            channels = ArtistService.get_channels()

            context = {
                **ArtistPresenter.base(),
                "page": "form",
                "mode": "create",
                "title": "Tambah Artist",
                "subtitle": "Tambahkan artist baru ke channel",
                "channels": channels,
                "artist": None,
                "is_edit": False,
                "form_action": "/admin/artists",
                "form_method": "POST",
                "button_text": "Simpan Artist",
            }

            # Add breadcrumb
            context = ArtistPresenter.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Artists", "url": "/admin/artists"},
                {"label": "Tambah Artist", "url": "#", "active": True},
            ])

            return context

        except Exception as e:
            logger.error(f"Error in create presenter: {e}")
            return {
                **ArtistPresenter.base(),
                "page": "form",
                "mode": "create",
                "title": "Tambah Artist",
                "subtitle": "Tambahkan artist baru ke channel",
                "channels": [],
                "artist": None,
                "error": str(e),
            }

    # =====================================================
    # FORM EDIT
    # =====================================================

    @staticmethod
    def edit(
        artist_id: int,
    ) -> Dict[str, Any]:
        """
        Data form edit artist.
        """
        try:
            artist = ArtistService.get_detail(artist_id)
            
            if not artist:
                raise ArtistNotFoundError(artist_id=artist_id)

            channels = ArtistService.get_channels()

            context = {
                **ArtistPresenter.base(),
                "page": "form",
                "mode": "edit",
                "title": "Edit Artist",
                "subtitle": f"Perbarui informasi artist: {artist.get('name', '')}",
                "artist": artist,
                "channels": channels,
                "is_edit": True,
                "form_action": f"/admin/artists/{artist_id}",
                "form_method": "PUT",
                "button_text": "Update Artist",
            }

            # Add breadcrumb
            context = ArtistPresenter.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Artists", "url": "/admin/artists"},
                {"label": f"Edit: {artist.get('name', '')}", "url": "#", "active": True},
            ])

            return context

        except ArtistNotFoundError:
            logger.error(f"Artist not found for edit: {artist_id}")
            return {
                **ArtistPresenter.base(),
                "page": "error",
                "title": "Artist Tidak Ditemukan",
                "subtitle": "Artist yang ingin diedit tidak ditemukan",
                "error": f"Artist dengan ID {artist_id} tidak ditemukan",
            }
        except Exception as e:
            logger.error(f"Error in edit presenter: {e}")
            return {
                **ArtistPresenter.base(),
                "page": "error",
                "title": "Error",
                "subtitle": "Terjadi kesalahan",
                "error": str(e),
            }

    # =====================================================
    # CHANNEL VIEW
    # =====================================================

    @staticmethod
    def channel(
        cursor,
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Artist berdasarkan channel.
        """
        try:
            channel = ArtistService.get_channel(
                cursor,
                channel_id,
            )

            if not channel:
                raise ChannelNotFoundError(channel_id=channel_id)

            statistics = ArtistService.statistics(
                channel_id=channel_id,
            )

            # Get artists in channel
            artists = ArtistService.get_by_channel(
                channel_id=channel_id,
                limit=100,
            )

            context = {
                **ArtistPresenter.base(),
                "page": "channel",
                "title": f'Artists - {channel.get("name", "Channel")}',
                "subtitle": f"Artists dalam channel {channel.get('name', '')}",
                "channel": channel,
                "statistics": statistics,
                "artists": artists,
            }

            # Add breadcrumb
            context = ArtistPresenter.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Artists", "url": "/admin/artists"},
                {"label": channel.get('name', 'Channel'), "url": "#", "active": True},
            ])

            return context

        except ChannelNotFoundError:
            logger.error(f"Channel not found: {channel_id}")
            return {
                **ArtistPresenter.base(),
                "page": "error",
                "title": "Channel Tidak Ditemukan",
                "subtitle": "Channel yang Anda cari tidak ditemukan",
                "error": f"Channel dengan ID {channel_id} tidak ditemukan",
            }
        except Exception as e:
            logger.error(f"Error in channel presenter: {e}")
            return {
                **ArtistPresenter.base(),
                "page": "error",
                "title": "Error",
                "subtitle": "Terjadi kesalahan",
                "error": str(e),
            }

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def statistics(
        channel_id: Optional[int] = None,
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """
        Halaman statistik artist.
        """
        try:
            stats = ArtistService.statistics(
                channel_id=channel_id,
                detailed=detailed,
            )

            # Get top artists if detailed
            top_artists = []
            if detailed:
                top_artists = ArtistService.top_artists(
                    channel_id=channel_id,
                    limit=10,
                    min_songs=1,
                )

            context = {
                **ArtistPresenter.base(),
                "page": "statistics",
                "title": "Statistik Artist",
                "subtitle": "Statistik dan analisis artist",
                "statistics": stats,
                "top_artists": top_artists,
                "channel_id": channel_id,
                "detailed": detailed,
            }

            # Add breadcrumb
            context = ArtistPresenter.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Artists", "url": "/admin/artists"},
                {"label": "Statistics", "url": "#", "active": True},
            ])

            return context

        except Exception as e:
            logger.error(f"Error in statistics presenter: {e}")
            return {
                **ArtistPresenter.base(),
                "page": "statistics",
                "title": "Statistik Artist",
                "subtitle": "Statistik dan analisis artist",
                "statistics": {},
                "top_artists": [],
                "error": str(e),
            }

    # =====================================================
    # BULK OPERATIONS
    # =====================================================

    @staticmethod
    def bulk_operations() -> Dict[str, Any]:
        """
        Halaman bulk operations artist.
        """
        try:
            channels = ArtistService.get_channels()

            context = {
                **ArtistPresenter.base(),
                "page": "bulk",
                "title": "Bulk Operations Artist",
                "subtitle": "Operasi massal untuk artist",
                "channels": channels,
            }

            # Add breadcrumb
            context = ArtistPresenter.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Artists", "url": "/admin/artists"},
                {"label": "Bulk Operations", "url": "#", "active": True},
            ])

            return context

        except Exception as e:
            logger.error(f"Error in bulk operations presenter: {e}")
            return {
                **ArtistPresenter.base(),
                "page": "bulk",
                "title": "Bulk Operations Artist",
                "subtitle": "Operasi massal untuk artist",
                "channels": [],
                "error": str(e),
            }

    # =====================================================
    # BULK RESPONSE
    # =====================================================

    @staticmethod
    def bulk_response(
        result: Dict[str, Any],
        action: str = "processed"
    ) -> Dict[str, Any]:
        """
        Format response untuk bulk operations.
        """
        return {
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "data": result.get('details', {}),
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }

    # =====================================================
    # HELPER METHODS
    # =====================================================

    @staticmethod
    def format_artist_for_table(artist: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format artist data for table display.
        """
        return {
            "id": artist.get('id'),
            "name": artist.get('name', ''),
            "channel_id": artist.get('channel_id'),
            "channel_name": artist.get('channel_name', ''),
            "song_count": artist.get('song_count', 0),
            "uploaded_songs": artist.get('uploaded_songs', 0),
            "pending_songs": artist.get('pending_songs', 0),
            "created_at": artist.get('created_at'),
            "created_at_formatted": (
                artist.get('created_at').strftime('%Y-%m-%d %H:%M')
                if artist.get('created_at')
                else '-'
            ),
            "updated_at": artist.get('updated_at'),
            "updated_at_formatted": (
                artist.get('updated_at').strftime('%Y-%m-%d %H:%M')
                if artist.get('updated_at')
                else '-'
            ),
            "status_badge": (
                '<span class="badge bg-success">Active</span>'
                if artist.get('song_count', 0) > 0
                else '<span class="badge bg-secondary">Inactive</span>'
            ),
        }

    @staticmethod
    def format_stats_for_display(stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format statistics for dashboard display.
        """
        total_artists = stats.get('total_artists', 0)
        artists_with_songs = stats.get('artists_with_songs', 0)
        
        return {
            "total_artists": total_artists,
            "total_songs": stats.get('total_songs', 0),
            "active_channels": stats.get('active_channels', 0),
            "artists_with_songs": artists_with_songs,
            "artists_without_songs": stats.get('artists_without_songs', 0),
            "avg_songs_per_artist": stats.get('avg_songs_per_artist', 0),
            "utilization_rate": (
                round((artists_with_songs / total_artists * 100), 2)
                if total_artists > 0
                else 0
            ),
        }

    # =====================================================
    # ERROR RESPONSES
    # =====================================================

    @staticmethod
    def error(
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format error response for UI.
        """
        return {
            **ArtistPresenter.base(),
            "error": True,
            "error_message": message,
            "status_code": status_code,
            "details": details or {},
            "page": "error",
            "title": "Error",
        }

    @staticmethod
    def not_found(
        message: str = "Artist tidak ditemukan"
    ) -> Dict[str, Any]:
        """
        Format 404 response for UI.
        """
        return ArtistPresenter.error(message, status_code=404)