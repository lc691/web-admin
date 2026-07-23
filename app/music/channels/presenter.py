"""
Channel Presenter - Complete Implementation

Presenter layer untuk Channel dengan:
- Context generation untuk templates
- Data formatting untuk UI
- Statistics presentation
- Bulk operation responses
- Consistent structure for views
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

from app.music.services.channels.service import ChannelService
from app.music.services.channels.mapper import ChannelMapper
from app.music.services.channels.exceptions import ChannelNotFoundError

from app.music.channels.schemas import ChannelResponse, ChannelDashboardStats

logger = logging.getLogger(__name__)


class ChannelPresenter:
    """
    Presenter halaman Channel.
    
    Menangani:
    - Context untuk template rendering
    - Formatting data untuk UI
    - Statistics aggregation
    - Bulk operation responses
    """
    
    # =====================================================
    # CONSTANTS
    # =====================================================
    
    MODULE = "channels"
    ICON = "ti ti-brand-youtube"
    MODULE_NAME = "Channels"
    MODULE_DESCRIPTION = "Kelola akun SoundOn Channel"
    
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
    
    # Status icons for UI
    STATUS_ICONS = {
        'released': 'fas fa-check-circle',
        'unreleased': 'fas fa-clock',
        'scheduled': 'fas fa-calendar-alt',
        'review': 'fas fa-eye',
        'approved': 'fas fa-check-double',
        'live': 'fas fa-broadcast',
        'take_down': 'fas fa-ban',
        'topic': 'fas fa-tag',
        'draft': 'fas fa-pen-fancy',
        'no_ads': 'fas fa-ad',
    }
    
    # Activity level colors
    LEVEL_COLORS = {
        'Highly Active': 'success',
        'Active': 'primary',
        'Moderately Active': 'info',
        'Low Activity': 'warning',
        'Inactive': 'secondary',
    }
    
    # =====================================================
    # BASE CONTEXT
    # =====================================================
    
    @classmethod
    def base(cls) -> Dict[str, Any]:
        """
        Context dasar semua halaman Channel.
        
        Returns:
            Dict with base context
        """
        return {
            "module": cls.MODULE,
            "icon": cls.ICON,
            "module_name": cls.MODULE_NAME,
            "module_description": cls.MODULE_DESCRIPTION,
            "status_colors": cls.STATUS_COLORS,
            "status_icons": cls.STATUS_ICONS,
            "level_colors": cls.LEVEL_COLORS,
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
        
        Args:
            context: Base context
            breadcrumb: List of breadcrumb items
            
        Returns:
            Context with breadcrumb
        """
        context['breadcrumb'] = breadcrumb
        return context
    
    # =====================================================
    # INDEX / LIST
    # =====================================================
    
    @classmethod
    def index(
        cls,
        cursor = None,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Presenter untuk halaman index/list channels.
        
        Args:
            cursor: Database cursor (optional)
            filter_params: Filter parameters (optional)
            
        Returns:
            Context for index page
        """
        context = {
            **cls.base(),
            "page": "index",
            "title": "Channels",
            "subtitle": "Kelola akun SoundOn Channel",
            "view": "list",
        }
        
        # Add breadcrumb
        context = cls.with_breadcrumb(context, [
            {"label": "Dashboard", "url": "/admin/dashboard"},
            {"label": "Channels", "url": "/admin/channels", "active": True},
        ])
        
        # Get statistics if cursor provided
        if cursor:
            try:
                stats = ChannelService.get_statistics(cursor, detailed=False)
                if stats.get('success'):
                    context['stats'] = stats.get('data', {})
            except Exception as e:
                logger.error(f"Error getting channel statistics: {e}")
                context['stats'] = {}
        
        # Add filter options
        context['filter_options'] = {
            'vermuk': [{'value': True, 'label': 'Vermuk'}, {'value': False, 'label': 'Normal'}],
            'has_artists': [{'value': True, 'label': 'With Artists'}, {'value': False, 'label': 'Without Artists'}],
            'has_songs': [{'value': True, 'label': 'With Songs'}, {'value': False, 'label': 'Without Songs'}],
        }
        
        return context
    
    # =====================================================
    # CREATE
    # =====================================================
    
    @classmethod
    def create(cls) -> Dict[str, Any]:
        """
        Presenter untuk halaman create channel.
        
        Returns:
            Context for create page
        """
        context = {
            **cls.base(),
            "page": "form",
            "mode": "create",
            "title": "Tambah Channel",
            "subtitle": "Tambahkan channel baru ke sistem",
            "channel": None,
            "is_edit": False,
            "form_action": "/admin/channels",
            "form_method": "POST",
            "button_text": "Simpan Channel",
        }
        
        # Add breadcrumb
        context = cls.with_breadcrumb(context, [
            {"label": "Dashboard", "url": "/admin/dashboard"},
            {"label": "Channels", "url": "/admin/channels"},
            {"label": "Tambah Channel", "url": "#", "active": True},
        ])
        
        return context
    
    # =====================================================
    # EDIT
    # =====================================================
    
    @classmethod
    def edit(
        cls,
        cursor,
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Presenter untuk halaman edit channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Context for edit page
            
        Raises:
            ChannelNotFoundError: If channel not found
        """
        try:
            # Get channel detail
            result = ChannelService.get_detail(cursor, channel_id)
            
            if not result.get('success'):
                raise ChannelNotFoundError(channel_id=channel_id)
            
            channel = result.get('data', {})
            
            context = {
                **cls.base(),
                "page": "form",
                "mode": "edit",
                "title": "Edit Channel",
                "subtitle": f"Perbarui informasi channel: {channel.get('name', '')}",
                "channel": channel,
                "is_edit": True,
                "form_action": f"/admin/channels/{channel_id}",
                "form_method": "PUT",
                "button_text": "Update Channel",
            }
            
            # Add breadcrumb
            context = cls.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Channels", "url": "/admin/channels"},
                {"label": f"Edit: {channel.get('name', '')}", "url": "#", "active": True},
            ])
            
            return context
            
        except ChannelNotFoundError as e:
            logger.error(f"Channel not found for edit: {channel_id}")
            raise
        except Exception as e:
            logger.error(f"Error editing channel {channel_id}: {e}")
            raise
    
    # =====================================================
    # DETAIL / VIEW
    # =====================================================
    
    @classmethod
    def detail(
        cls,
        cursor,
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Presenter untuk halaman detail channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Context for detail page
            
        Raises:
            ChannelNotFoundError: If channel not found
        """
        try:
            # Get channel detail with stats
            result = ChannelService.get_detail(cursor, channel_id)
            
            if not result.get('success'):
                raise ChannelNotFoundError(channel_id=channel_id)
            
            channel = result.get('data', {})
            
            # Get activity score
            activity = None
            try:
                activity_result = ChannelService.get_activity_score(cursor, channel_id)
                if activity_result.get('success'):
                    activity = activity_result.get('data')
            except Exception as e:
                logger.warning(f"Error getting activity score: {e}")
            
            # Get status breakdown
            status_breakdown = None
            try:
                status_result = ChannelService.get_status_breakdown(cursor, channel_id)
                if status_result.get('success'):
                    status_breakdown = status_result.get('data')
            except Exception as e:
                logger.warning(f"Error getting status breakdown: {e}")
            
            context = {
                **cls.base(),
                "page": "detail",
                "title": channel.get('name', 'Channel Detail'),
                "subtitle": "Informasi Lengkap Channel",
                "channel": channel,
                "activity": activity,
                "status_breakdown": status_breakdown,
                "can_edit": True,
                "can_delete": True,
            }
            
            # Add breadcrumb
            context = cls.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Channels", "url": "/admin/channels"},
                {"label": channel.get('name', 'Detail'), "url": "#", "active": True},
            ])
            
            return context
            
        except ChannelNotFoundError as e:
            logger.error(f"Channel not found for detail: {channel_id}")
            raise
        except Exception as e:
            logger.error(f"Error getting channel detail {channel_id}: {e}")
            raise
    
    # =====================================================
    # STATISTICS
    # =====================================================
    
    @classmethod
    def statistics(
        cls,
        cursor,
        detailed: bool = False,
        period: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Presenter untuk halaman statistics channel.
        
        Args:
            cursor: Database cursor
            detailed: Get detailed statistics
            period: Period for data (daily, weekly, monthly)
            
        Returns:
            Statistics context
        """
        try:
            # Get statistics
            result = ChannelService.get_statistics(cursor, detailed=detailed)
            stats = result.get('data', {}) if result.get('success') else {}
            
            # Get daily stats if requested
            daily_stats = None
            if detailed:
                try:
                    daily_result = ChannelService.get_daily_stats(cursor, days=30)
                    if daily_result.get('success'):
                        daily_stats = daily_result.get('data')
                except Exception as e:
                    logger.warning(f"Error getting daily stats: {e}")
            
            # Get top channels
            top_channels = None
            try:
                top_result = ChannelService.get_top_channels(cursor, limit=10)
                if top_result.get('success'):
                    top_channels = top_result.get('data')
            except Exception as e:
                logger.warning(f"Error getting top channels: {e}")
            
            context = {
                **cls.base(),
                "page": "statistics",
                "title": "Channel Statistics",
                "subtitle": "Statistik dan Analisis Channel",
                "stats": stats,
                "daily_stats": daily_stats,
                "top_channels": top_channels,
                "detailed": detailed,
                "period": period,
            }
            
            # Add breadcrumb
            context = cls.with_breadcrumb(context, [
                {"label": "Dashboard", "url": "/admin/dashboard"},
                {"label": "Channels", "url": "/admin/channels"},
                {"label": "Statistics", "url": "#", "active": True},
            ])
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                **cls.base(),
                "page": "statistics",
                "title": "Channel Statistics",
                "subtitle": "Statistik dan Analisis Channel",
                "stats": {},
                "error": str(e),
            }
    
    # =====================================================
    # BULK OPERATIONS
    # =====================================================
    
    @classmethod
    def bulk_delete_response(
        cls,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format response for bulk delete operation.
        
        Args:
            result: Result from bulk delete
            
        Returns:
            Formatted response for UI
        """
        return {
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "data": result.get('data', {}),
            "action": "bulk_delete",
            "timestamp": datetime.now().isoformat(),
        }
    
    @classmethod
    def bulk_vermuk_response(
        cls,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format response for bulk vermuk update.
        
        Args:
            result: Result from bulk vermuk update
            
        Returns:
            Formatted response for UI
        """
        return {
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "data": result.get('data', {}),
            "action": "bulk_vermuk",
            "timestamp": datetime.now().isoformat(),
        }
    
    # =====================================================
    # HELPER METHODS
    # =====================================================
    
    @staticmethod
    def format_channel_for_table(channel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format channel data for table display.
        
        Args:
            channel: Channel data
            
        Returns:
            Formatted channel for table
        """
        return {
            "id": channel.get('id'),
            "name": channel.get('name', ''),
            "email": channel.get('email', ''),
            "vermuk": channel.get('vermuk', False),
            "vermuk_badge": "Vermuk" if channel.get('vermuk') else "Normal",
            "vermuk_color": "danger" if channel.get('vermuk') else "secondary",
            "total_artists": channel.get('total_artists', 0),
            "total_songs": channel.get('total_songs', 0),
            "uploaded_songs": channel.get('uploaded_songs', 0),
            "pending_songs": channel.get('pending_songs', 0),
            "created_at": channel.get('created_at'),
            "created_at_formatted": (
                channel.get('created_at').strftime('%Y-%m-%d %H:%M')
                if channel.get('created_at')
                else '-'
            ),
            "updated_at": channel.get('updated_at'),
            "updated_at_formatted": (
                channel.get('updated_at').strftime('%Y-%m-%d %H:%M')
                if channel.get('updated_at')
                else '-'
            ),
        }
    
    @staticmethod
    def format_stats_for_display(stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format statistics for dashboard display.
        
        Args:
            stats: Statistics data
            
        Returns:
            Formatted statistics
        """
        return {
            "total_channels": stats.get('total_channels', 0),
            "total_vermuk": stats.get('total_vermuk', 0),
            "total_normal": stats.get('total_normal', 0),
            "total_artists": stats.get('total_artists', 0),
            "total_songs": stats.get('total_songs', 0),
            "uploaded_songs": stats.get('uploaded_songs', 0),
            "pending_songs": stats.get('pending_songs', 0),
            "takedown_songs": stats.get('takedown_songs', 0),
            "utilization_rate": stats.get('utilization_rate', 0),
            "avg_songs_per_channel": stats.get('avg_songs_per_channel', 0),
            "avg_artists_per_channel": stats.get('avg_artists_per_channel', 0),
            "status_breakdown": stats.get('status_breakdown', {}),
        }
    
    @staticmethod
    def format_activity_for_display(activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format activity data for display.
        
        Args:
            activity: Activity data
            
        Returns:
            Formatted activity data
        """
        if not activity:
            return {}
        
        return {
            "level": activity.get('level', 'Inactive'),
            "level_color": ChannelPresenter.LEVEL_COLORS.get(
                activity.get('level', 'Inactive'), 'secondary'
            ),
            "overall_score": activity.get('overall_score', 0),
            "recency_score": activity.get('recency_score', 0),
            "consistency_score": activity.get('consistency_score', 0),
            "engagement_score": activity.get('engagement_score', 0),
            "growth_score": activity.get('growth_score', 0),
            "recent_songs": activity.get('recent_songs', 0),
            "total_songs": activity.get('total_songs', 0),
            "total_artists": activity.get('total_artists', 0),
            "upload_rate": activity.get('upload_rate', 0),
            "avg_songs_per_month": activity.get('avg_songs_per_month', 0),
            "last_activity": activity.get('last_activity'),
            "last_activity_formatted": (
                activity.get('last_activity').strftime('%Y-%m-%d %H:%M')
                if activity.get('last_activity')
                else '-'
            ),
        }
    
    @classmethod
    def get_status_badge(cls, status: str) -> Dict[str, str]:
        """
        Get status badge configuration.
        
        Args:
            status: Status name
            
        Returns:
            Dict with color and icon
        """
        return {
            "color": cls.STATUS_COLORS.get(status, 'secondary'),
            "icon": cls.STATUS_ICONS.get(status, 'fas fa-circle'),
            "label": status.replace('_', ' ').title(),
        }
    
    @classmethod
    def get_activity_level_badge(cls, level: str) -> Dict[str, str]:
        """
        Get activity level badge configuration.
        
        Args:
            level: Activity level name
            
        Returns:
            Dict with color and label
        """
        return {
            "color": cls.LEVEL_COLORS.get(level, 'secondary'),
            "label": level,
        }
    
    # =====================================================
    # ERROR RESPONSES
    # =====================================================
    
    @classmethod
    def error(
        cls,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format error response for UI.
        
        Args:
            message: Error message
            status_code: HTTP status code
            details: Error details
            
        Returns:
            Error context
        """
        return {
            **cls.base(),
            "error": True,
            "error_message": message,
            "status_code": status_code,
            "details": details or {},
            "page": "error",
            "title": "Error",
        }
    
    @classmethod
    def not_found(
        cls,
        message: str = "Channel tidak ditemukan"
    ) -> Dict[str, Any]:
        """
        Format 404 response for UI.
        
        Args:
            message: Error message
            
        Returns:
            404 error context
        """
        return cls.error(message, status_code=404)