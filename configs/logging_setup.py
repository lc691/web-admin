import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from colorama import Fore, Style
from colorama import init as colorama_init
from pytz import timezone

colorama_init(autoreset=True)  # init sekali saja


# =====================================================
# === FORMATTER =======================================
# =====================================================
class JakartaFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(
            record.created,
            tz=timezone("Asia/Jakarta"),
        )
        return dt.strftime(datefmt) if datefmt else dt.isoformat()


class ColoredFormatter(JakartaFormatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


# =====================================================
# === SETUP LOGGER ====================================
# =====================================================
def setup_logger(
    name: str | None = None,
    log_dir: str = "logs",
    level: int = logging.INFO,
):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    logger = logging.getLogger(name) if name else logging.getLogger()

    # =================================================
    # 🔇 SILENCE UVICORN & WEB NOISE (PENTING)
    # =================================================
    for noisy in (
        "httpx",
        "apscheduler",
        "asyncio",
        "uvicorn.access",
        "uvicorn.error",
        "starlette",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # =================================================
    logger.setLevel(level)
    logger.propagate = False

    # Clear handler lama (hindari duplikasi)
    if logger.handlers:
        logger.handlers.clear()

    # =================================================
    # FILE HANDLER (rotasi harian)
    # =================================================
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True,
    )
    file_handler.setFormatter(
        JakartaFormatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(file_handler)

    # =================================================
    # CONSOLE HANDLER (warna + WIB)
    # =================================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        ColoredFormatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(console_handler)

    return logger


# =====================================================
# === USAGE ===========================================
# =====================================================
log = setup_logger(__name__)
log.info("✅ Logger siap dipakai (low-IO mode)")
