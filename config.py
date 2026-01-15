# config.py

import os
from typing import List, Tuple

from dotenv import load_dotenv

load_dotenv()  # Penting: ini harus dipanggil sebelum akses os.environ


def get_env(name, cast=str):
    try:
        value = os.environ[name]
        if cast is bool:
            return value.lower() in ("1", "true", "yes", "on")
        return cast(value)
    except KeyError:
        raise RuntimeError(f"❌ ENV '{name}' tidak ditemukan!")
    except ValueError:
        raise RuntimeError(f"❌ ENV '{name}' harus bertipe {cast.__name__}!")


# === Telegram Bot Config ===
API_ID = get_env("API_ID", int)
API_HASH = get_env("API_HASH")
BOT_TOKEN_KELOLA = get_env("BOT_TOKEN_KELOLA")
BOT_TOKEN = get_env("BOT_TOKEN")
BOT_TOKEN_UTBK = get_env("BOT_TOKEN_UTBK")
TRAKTEER_SECRET_KEY = get_env("TRAKTEER_SECRET_KEY")


# === PostgreSQL Config ===
PGDATABASE = get_env("PGDATABASE")
PGUSER = get_env("PGUSER")
PGPASSWORD = get_env("PGPASSWORD")
PGHOST = get_env("PGHOST")
PGPORT = get_env("PGPORT", int)

# === Channel & Admin ===
DB_DRAMA = get_env("DB_DRAMA", int)
POSTING_CHANNEL = get_env("POSTING_CHANNEL", int)
POSTING_UTBK = get_env("POSTING_UTBK")

admin_ids_raw = get_env("ADMIN_IDS", str)
if admin_ids_raw:
    ADMIN_IDS = [
        int(x.strip()) for x in admin_ids_raw.split(",") if x.strip().isdigit()
    ]
else:
    ADMIN_IDS = []

REQUIRED_CHANNELS: List[Tuple[str, str]] = [
    ("dracinshort", "https://t.me/dracinshort"),
    ("dramacinavip", "https://t.me/dramacinavip"),
]

REQUEST_CHANNELS: List[Tuple[str, str]] = [
    ("requestdcstv", "t.me/requestdcstv"),
]

REQUIRED_CHANNELS_UTBK: List[Tuple[str, str]] = [
    ("dcstutbk2025", "https://t.me/dcstutbk2025"),  # tanpa @
]

SMTP_USER = get_env("SMTP_USER")
SMTP_PASS = get_env("SMTP_PASS")


adding_channel_users = set()

SPECIAL_DONORS = {
    "vipuser@example.com": "🎉 Hai VIP! Terima kasih banyak atas dukungannya!",
    "admin@project.com": "🙏 Terima kasih, Admin! Donasimu sangat berarti.",
    "sahabat@supporter.com": "💖 Terima kasih sahabat! Kami sangat menghargainya.",
}

UPLOAD_DELAY = 1.5  # delay antar file dalam detik

# config.py
DEFAULT_THUMBNAIL_FILE_ID = "AgACAgUAAyEFAASX5fXZAAICSWhv9v-vJUb-mdE6UpJxet09EHBkAALDwjEblA6BVyP8WR-uIemcAAgBAAMCAAN5AAceBA"
