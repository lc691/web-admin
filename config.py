# config.py

from __future__ import annotations

import os
from typing import Any, Callable

from dotenv import load_dotenv

from configs.logging_setup import log  # import harus di atas (fix E402)

# =====================
# ENV LOADING
# =====================
load_dotenv()


# =====================
# HELPERS
# =====================
def require_env(name: str, cast: Callable[[str], Any] = str) -> Any:
    value = os.getenv(name)

    if value is None or value == "":
        raise RuntimeError(f"ENV '{name}' is required")

    try:
        return cast(value)
    except Exception as err:
        raise RuntimeError(f"ENV '{name}' must be {cast.__name__}") from err


def optional_env(
    name: str,
    default: Any = None,
    cast: Callable[[str], Any] = str,
) -> Any:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    try:
        return cast(value)
    except Exception:
        log.warning("ENV %s invalid, fallback to default", name)
        return default


def parse_int_list(raw: str | None) -> list[int]:
    if not raw:
        return []

    return [int(x) for x in raw.split(",") if x.strip().isdigit()]


# =====================
# MODE
# =====================
MODE: str = optional_env("MODE", "production")
IS_DEV: bool = MODE == "development"


# =====================
# TELEGRAM CORE
# =====================
API_ID: int = require_env("API_ID", int)
API_HASH: str = require_env("API_HASH")

BOT_TOKEN: str = optional_env("BOT_TOKEN_DEV") if IS_DEV else require_env("BOT_TOKEN")

BOT_USERNAME: str = optional_env("BOT_USERNAME", "drac1n_bot")


# =====================
# MULTI BOT TOKEN
# =====================
BOT_TOKEN_KELOLA: str | None = optional_env("BOT_TOKEN_KELOLA")
BOT_TOKEN_UTBK: str | None = optional_env("BOT_TOKEN_UTBK")
BOT_TOKEN_CARI: str | None = optional_env("BOT_TOKEN_CARI")


# =====================
# DATABASE
# =====================
PGDATABASE: str = require_env("PGDATABASE")
PGUSER: str = require_env("PGUSER")
PGPASSWORD: str = require_env("PGPASSWORD")
PGHOST: str = optional_env("PGHOST", "127.0.0.1")
PGPORT: int = optional_env("PGPORT", 5432, int)


# =====================
# CHANNEL / GROUP
# =====================
DB_DRAMA: int = optional_env("DB_DRAMA", 0, int)
POSTING_TEST: int = optional_env("POSTING_TEST", 0, int)
POSTING_CHANNEL: int = optional_env("POSTING_CHANNEL", 0, int)
GROUP_DISKUSI: int = optional_env("GROUP_DISKUSI", 0, int)

BACKUP_CHANNEL: str = optional_env("BACKUP_CHANNEL", "@dramacinavip")


# =====================
# ADMIN
# =====================
ADMIN_IDS: list[int] = parse_int_list(optional_env("ADMIN_IDS", ""))


# =====================
# LIMIT & VIP
# =====================
DAILY_FREE_LIMIT: int = optional_env("DAILY_FREE_LIMIT", 5, int)
UNLIMITED: int = optional_env("UNLIMITED", 999999, int)


# =====================
# PAYMENT
# =====================
TRAKTEER_SECRET_KEY: str | None = optional_env("TRAKTEER_SECRET_KEY")
MANUAL_TRX_TOKEN: str | None = optional_env("MANUAL_TRX_TOKEN")


# =====================
# SMTP
# =====================
SMTP_USER: str | None = optional_env("SMTP_USER")
SMTP_PASS: str | None = optional_env("SMTP_PASS")


# =====================
# CRON / WORKER
# =====================
CLEANUP_INTERVAL: int = optional_env("CLEANUP_INTERVAL", 600, int)
UPLOAD_DELAY: float = optional_env("UPLOAD_DELAY", 1.5, float)


# =====================
# STATIC CONFIG
# =====================
TARGET_CHANNELS: list[str] = [
    "reelshortx",
    "dramawavee",
    "netshortt",
    "listfilmdcstv",
]

REQUIRED_CHANNELS: list[tuple[str, str]] = [
    ("dracinshort", "https://t.me/dracinshort"),
    ("dramacinavip", "https://t.me/dramacinavip"),
    ("dracinshortgroup", "https://t.me/dracinshortgroup"),
]

REQUEST_CHANNELS: list[tuple[str, str]] = [
    ("requestdcstv", "https://t.me/requestdcstv"),
]

REQUIRED_CHANNELS_UTBK: list[tuple[str, str]] = [
    ("dcstutbk2025", "https://t.me/dcstutbk2025"),
]


# =====================
# SESSION (WORKER)
# =====================
BOT_SESSION: dict[str, Any] = {
    "name": "vip-bot-cron",
    "api_id": API_ID,
    "api_hash": API_HASH,
    "bot_token": BOT_TOKEN,
}


# =====================
# OPTIONAL FLAGS
# =====================
SPECIAL_DONORS: set[int] = set()

DEFAULT_THUMBNAIL_FILE_ID: str | None = optional_env("DEFAULT_THUMBNAIL_FILE_ID")

VIP_UPGRADE_URL: str | None = optional_env("VIP_UPGRADE_URL")


# =====================
# SAFE DEBUG SUMMARY
# =====================
if IS_DEV:
    log.info("Running in %s mode", MODE.upper())
    log.info("Bot: %s", BOT_USERNAME)
    log.info("DB: %s@%s:%s/%s", PGUSER, PGHOST, PGPORT, PGDATABASE)
    log.info("Admins: %s", ADMIN_IDS)
