from pathlib import Path
from typing import Tuple, Optional, List, Any, Union
import json
import ast

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ================================
    # Core Config
    # ================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ================================
    # Mode / Runtime
    # ================================
    MODE: str = "production"
    RUNTIME_MODE: str = "polling"
    TZ: str = "Asia/Jakarta"

    # ================================
    # App
    # ================================
    APP_NAME: str = "SoundON Admin"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ================================
    # Server
    # ================================
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # ================================
    # Security
    # ================================
    SECRET_KEY: str = "super-secret-random-string"
    SESSION_SECRET_KEY: str = "super-secret-session-key-123456"
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # ================================
    # Auth Cookie
    # ================================
    AUTH_COOKIE_NAME: str = "auth_session"
    AUTH_COOKIE_MAX_AGE: int = 86400
    AUTH_COOKIE_HTTP_ONLY: bool = True
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_SAMESITE: str = "lax"

    # ================================
    # Admin
    # ================================
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = "$2b$12$XUgMk9ulFIyjcJWKwkhojOgONwLOCvczjV1oJazqZf/xpzv1CbueC"
    ADMIN_IDS: str = "7294710696"

    @property
    def admin_ids_list(self) -> List[int]:
        """Convert ADMIN_IDS string to list of integers"""
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    # ================================
    # PostgreSQL
    # ================================
    PGHOST: str = "127.0.0.1"
    PGPORT: int = 5432
    PGDATABASE: str = "botdb"
    PGUSER: str = "botuser"
    PGPASSWORD: str = "noFWOLNMzIJcAwDmwcuhMhzccAWhpelx"
    DATABASE_URL: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Generate database URL dari komponen PostgreSQL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"

    # ================================
    # Telegram
    # ================================
    API_ID: int = 28806098
    API_HASH: str = "896d1ce129959745f4f8e412b353834f"
    BOT_TOKEN: str = "8132937843:AAFO2-Deq2odWKLmHzyRPp1_caG6xEpgGaA"
    BOT_TOKEN_KELOLA: Optional[str] = "7578429351:AAF5wHVdpob7MVmhbxC6R44R5XWRh_ENpbQ"
    BOT_TOKEN_CARI: Optional[str] = "8293832999:AAHniiwh_NO7n4czJ73Q1K_DX9MHFX2NZpE"
    BOT_TOKEN_UTBK: Optional[str] = "7714074581:AAFOgSak4EKLSKOrOSMP-bM4oShoqkSYhzU"

    # ================================
    # Telegram Channels / Groups
    # ================================
    DB_DRAMA: str = "-1002548430297"
    POSTING_TEST: str = "-1002593474221"
    POSTING_CHANNEL: str = "-1002571436080"
    GROUP_DISKUSI: str = "-1002515868345"
    BACKUP_DCSTV: str = "-1002697569868"

    @property
    def channel_ids(self) -> dict:
        """Return all channel/group IDs as dict"""
        return {
            "db_drama": self.DB_DRAMA,
            "posting_test": self.POSTING_TEST,
            "posting_channel": self.POSTING_CHANNEL,
            "group_diskusi": self.GROUP_DISKUSI,
            "backup_dcstv": self.BACKUP_DCSTV,
        }

    # ================================
    # Limits
    # ================================
    DAILY_FREE_LIMIT: int = 10
    UNLIMITED: int = 9999

    # ================================
    # SMTP
    # ================================
    SMTP_USER: Optional[str] = "layardrama092@gmail.com"
    SMTP_PASS: Optional[str] = "rdgg iuni ifhi qvub"

    # ================================
    # Trakteer
    # ================================
    TRAKTEER_SECRET_KEY: Optional[str] = "trhook-4pDzVJaCCkS7nbqsIho7kkdF"
    MANUAL_TRX_TOKEN: Optional[str] = "supersecretmanualtoken"

    # ================================
    # Worker / Scheduler
    # ================================
    CLEANUP_INTERVAL: int = 600

    # ================================
    # Default Thumbnail
    # ================================
    DEFAULT_THUMBNAIL_FILE_ID: str = "AgACAgUAAyEFAASX5fXZAAICSWhv9v-vJUb-mdE6UpJxet09EHBkAALDwjEblA6BVyP8WR-uIemcAAgBAAMCAAN5AAceBA"

    # ================================
    # VIP Upgrade URL
    # ================================
    VIP_UPGRADE_URL: str = "https://t.me/drac1n_bot?start=vip"

    # ================================
    # Public Routes - Gunakan Union agar bisa menerima string atau tuple
    # ================================
    PUBLIC_PATHS: Union[str, Tuple[str, ...]] = '["/login","/logout","/register","/forgot-password","/health"]'
    PUBLIC_PATH_PREFIXES: Union[str, Tuple[str, ...]] = '["/static","/favicon","/assets","/css","/js","/images","/docs","/redoc","/openapi.json"]'
    PUBLIC_STARTSWITH: Union[str, Tuple[str, ...]] = '["/static","/favicon"]'
    PUBLIC_EXACT: Union[str, Tuple[str, ...]] = "[]"

    @field_validator('PUBLIC_PATHS', 'PUBLIC_PATH_PREFIXES', 'PUBLIC_STARTSWITH', 'PUBLIC_EXACT', mode='before')
    @classmethod
    def parse_json_field(cls, v: Any) -> Tuple[str, ...]:
        """Parse JSON string to tuple"""
        # Jika sudah tuple, return as-is
        if isinstance(v, tuple):
            return v
        
        # Jika string, coba parse
        if isinstance(v, str):
            # Coba parse JSON
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return tuple(parsed)
            except json.JSONDecodeError:
                pass
            
            # Coba parse dengan ast.literal_eval
            try:
                parsed = ast.literal_eval(v)
                if isinstance(parsed, list):
                    return tuple(parsed)
            except (ValueError, SyntaxError):
                pass
            
            # Jika single string (bukan array)
            return (v,) if v else tuple()
        
        # Jika list, convert ke tuple
        if isinstance(v, list):
            return tuple(v)
        
        # Default empty tuple
        return tuple()

    # ================================
    # CORS
    # ================================
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8080"]

    # ================================
    # Static
    # ================================
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"

    # ================================
    # Logging
    # ================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"
    LOG_DIR: str = "logs"

    # ================================
    # Telegram Notification (Opsional)
    # ================================
    TELEGRAM_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # ================================
    # Helper Methods
    # ================================
    def get_bot_tokens(self) -> dict:
        """Get all bot tokens"""
        return {
            "main": self.BOT_TOKEN,
            "kelola": self.BOT_TOKEN_KELOLA,
            "cari": self.BOT_TOKEN_CARI,
            "utbk": self.BOT_TOKEN_UTBK,
        }

    def get_public_paths(self) -> Tuple[str, ...]:
        """Get public paths as tuple"""
        if isinstance(self.PUBLIC_PATHS, tuple):
            return self.PUBLIC_PATHS
        return tuple()

    def get_public_prefixes(self) -> Tuple[str, ...]:
        """Get public path prefixes as tuple"""
        if isinstance(self.PUBLIC_PATH_PREFIXES, tuple):
            return self.PUBLIC_PATH_PREFIXES
        return tuple()

    def get_public_exact(self) -> Tuple[str, ...]:
        """Get public exact paths as tuple"""
        if isinstance(self.PUBLIC_EXACT, tuple):
            return self.PUBLIC_EXACT
        return tuple()

    def is_public_path(self, path: str) -> bool:
        """Check if a path is public"""
        # Check exact matches
        public_paths = self.get_public_paths()
        if path in public_paths:
            return True
        
        # Check exact matches from PUBLIC_EXACT
        public_exact = self.get_public_exact()
        if path in public_exact:
            return True
        
        # Check prefixes
        public_prefixes = self.get_public_prefixes()
        for prefix in public_prefixes:
            if path.startswith(prefix):
                return True
        
        return False


# Singleton instance
settings = Settings()