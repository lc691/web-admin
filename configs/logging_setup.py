import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from colorama import Fore, Style, init as colorama_init
from pytz import timezone

colorama_init(autoreset=True)

JAKARTA_TZ = timezone("Asia/Jakarta")


# =====================================================
# FORMATTER BASE (WIB)
# =====================================================
class JakartaFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=JAKARTA_TZ)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")


# =====================================================
# COLORED FORMATTER (CONSOLE ONLY)
# =====================================================
class ColoredFormatter(JakartaFormatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{levelname}{Style.RESET_ALL}"
        msg = super().format(record)
        record.levelname = levelname  # restore
        return msg


# =====================================================
# LOGGER SETUP
# =====================================================
def setup_logger(
    name: str = "app",
    log_dir: str = "logs",
    level: int = logging.INFO,
):
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Cegah double handler (penting di reload / import ulang)
    if logger.handlers:
        return logger

    # ---------------------
    # FILE HANDLER (ROTATE)
    # ---------------------
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        when="midnight",
        interval=1,
        backupCount=14,
        encoding="utf-8",
        utc=True,
    )
    file_handler.setFormatter(
        JakartaFormatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    )
    logger.addHandler(file_handler)

    # ---------------------
    # CONSOLE HANDLER
    # ---------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        ColoredFormatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(console_handler)

    # ---------------------
    # NOISE REDUCTION
    # ---------------------
    for noisy in ("uvicorn", "uvicorn.access", "httpx", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logger


# =====================================================
# GLOBAL LOGGER
# =====================================================
log = setup_logger("webhook")
