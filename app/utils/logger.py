"""
Logging Configuration untuk SoundON Admin Dashboard
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from colorama import Fore, Style, init as colorama_init
from pytz import timezone

from app.core.config import settings

colorama_init(autoreset=True)

JAKARTA_TZ = timezone("Asia/Jakarta")


# =====================================================
# FORMATTER BASE (WIB)
# =====================================================
class JakartaFormatter(logging.Formatter):
    """Custom formatter with Jakarta timezone"""
    
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=JAKARTA_TZ)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")


# =====================================================
# COLORED FORMATTER (CONSOLE ONLY)
# =====================================================
class ColoredFormatter(JakartaFormatter):
    """Colored formatter for console output"""
    
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }
    
    LEVEL_ICONS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    def format(self, record):
        original_levelname = record.levelname
        
        icon = self.LEVEL_ICONS.get(record.levelno, "")
        if icon:
            record.levelname = f"{icon} {record.levelname}"
        
        color = self.COLORS.get(record.levelno, "")
        if color:
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        
        msg = super().format(record)
        record.levelname = original_levelname
        
        return msg


# =====================================================
# JSON FORMATTER
# =====================================================
class JsonFormatter(JakartaFormatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        import json
        
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


# =====================================================
# TELEGRAM HANDLER
# =====================================================
class TelegramHandler(logging.Handler):
    """Handler untuk mengirim log error ke Telegram"""
    
    def __init__(self, token: str, chat_id: str, level=logging.ERROR):
        super().__init__(level)
        self.token = token
        self.chat_id = chat_id
    
    def emit(self, record):
        try:
            import httpx
            msg = self.format(record)
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            httpx.post(url, json={
                "chat_id": self.chat_id,
                "text": f"⚠️ *ERROR*\n```\n{msg[:4000]}\n```",
                "parse_mode": "Markdown"
            }, timeout=5.0)
        except Exception:
            pass


# =====================================================
# LOGGER SETUP
# =====================================================
def setup_logger(
    name: str = "soundon",
    log_dir: str = None,
    level: int = None,
    log_format: str = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_telegram: bool = False,
    telegram_token: Optional[str] = None,
    telegram_chat_id: Optional[str] = None,
):
    """Setup logger dengan konfigurasi dari settings"""
    # Gunakan settings jika tidak dioverride
    if log_dir is None:
        log_dir = settings.LOG_DIR
    if level is None:
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    if log_format is None:
        log_format = settings.LOG_FORMAT
    
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    # File Handler
    if enable_file:
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "app.log"),
            when="midnight",
            interval=1,
            backupCount=14,
            encoding="utf-8",
            utc=True,
        )
        
        if log_format == "json":
            file_formatter = JsonFormatter()
        else:
            file_formatter = JakartaFormatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error log
        error_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "error.log"),
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
            utc=True,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            JakartaFormatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
            )
        )
        logger.addHandler(error_handler)

    # Console Handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        
        if log_format == "json":
            console_formatter = JsonFormatter()
        else:
            console_formatter = ColoredFormatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S",
            )
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Telegram Handler
    if enable_telegram:
        token = telegram_token or settings.TELEGRAM_TOKEN
        chat_id = telegram_chat_id or settings.TELEGRAM_CHAT_ID
        if token and chat_id:
            telegram_handler = TelegramHandler(
                token=token,
                chat_id=chat_id,
                level=logging.ERROR,
            )
            logger.addHandler(telegram_handler)

    # Noise reduction
    for noisy in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "httpx",
        "asyncio",
        "sqlalchemy",
        "aiosqlite",
        "psycopg2",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logger


# =====================================================
# LOGGER FACTORY
# =====================================================
class LoggerFactory:
    """Factory for creating named loggers"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, **kwargs) -> logging.Logger:
        if name not in cls._loggers:
            cls._loggers[name] = setup_logger(name, **kwargs)
        return cls._loggers[name]
    
    @classmethod
    def configure_default(cls, **kwargs):
        for name, logger in cls._loggers.items():
            new_logger = setup_logger(name, **kwargs)
            cls._loggers[name] = new_logger


# =====================================================
# CONTEXT LOGGER
# =====================================================
class ContextLogger:
    """Logger with context (request ID, user, etc.)"""
    
    def __init__(self, logger: logging.Logger, context: dict = None):
        self.logger = logger
        self.context = context or {}
    
    def _log(self, level: int, msg: str, *args, **kwargs):
        extra = kwargs.get("extra", {})
        extra.update(self.context)
        kwargs["extra"] = extra
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)


# =====================================================
# GLOBAL LOGGER
# =====================================================
log = setup_logger("soundon")


# =====================================================
# FUNGSI BANTUAN
# =====================================================
def get_logger(name: str) -> logging.Logger:
    """Get logger by name"""
    return LoggerFactory.get_logger(name)


def get_context_logger(name: str, context: dict = None) -> ContextLogger:
    """Get context logger by name"""
    logger = get_logger(name)
    return ContextLogger(logger, context)