"""
Telegram Helpers untuk mengakses config Telegram
"""

from typing import Optional, Dict, List
from app.core.config import settings
from app.utils.logger import log


class TelegramConfig:
    """Helper untuk mengakses konfigurasi Telegram"""
    
    @staticmethod
    def get_bot_token(name: str = "main") -> Optional[str]:
        """Get bot token by name"""
        tokens = {
            "main": settings.BOT_TOKEN,
            "kelola": settings.BOT_TOKEN_KELOLA,
            "cari": settings.BOT_TOKEN_CARI,
            "utbk": settings.BOT_TOKEN_UTBK,
        }
        return tokens.get(name)
    
    @staticmethod
    def get_all_bots() -> Dict[str, str]:
        """Get all bot tokens"""
        return {
            "main": settings.BOT_TOKEN,
            "kelola": settings.BOT_TOKEN_KELOLA,
            "cari": settings.BOT_TOKEN_CARI,
            "utbk": settings.BOT_TOKEN_UTBK,
        }
    
    @staticmethod
    def get_channel_id(name: str) -> Optional[str]:
        """Get channel ID by name"""
        channels = {
            "db_drama": settings.DB_DRAMA,
            "posting_test": settings.POSTING_TEST,
            "posting_channel": settings.POSTING_CHANNEL,
            "group_diskusi": settings.GROUP_DISKUSI,
            "backup_dcstv": settings.BACKUP_DCSTV,
        }
        return channels.get(name)
    
    @staticmethod
    def get_all_channels() -> Dict[str, str]:
        """Get all channel IDs"""
        return settings.channel_ids
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in settings.admin_ids_list


# ================================
# FUNGSI BANTUAN
# ================================
def get_bot_token(name: str = "main") -> Optional[str]:
    """Get bot token by name"""
    return TelegramConfig.get_bot_token(name)


def get_channel_id(name: str) -> Optional[str]:
    """Get channel ID by name"""
    return TelegramConfig.get_channel_id(name)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return TelegramConfig.is_admin(user_id)