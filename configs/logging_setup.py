import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from colorama import Fore, Style
from colorama import init as colorama_init
from pytz import timezone

colorama_init(autoreset=True)  # sekali saja


class JakartaFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone("Asia/Jakarta"))
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()


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


def setup_logger(log_dir="logs", level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "bot.log")

    logger = logging.getLogger("drac1n")
    logger.setLevel(level)
    logger.propagate = False  # supaya tidak dobel log

    # Clear handler lama jika ada
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler (rotating daily)
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True,
    )
    file_formatter = JakartaFormatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (colored + WIB time)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Turunkan noise modul luar
    for noisy in ["pyrogram", "apscheduler", "httpx"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logger


log = logging.getLogger("drac1n")
