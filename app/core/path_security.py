from fastapi import Request
from app.core.config import settings
from app.utils.logger import log


def normalize(path: str) -> str:
    return (path or "").rstrip("/") or "/"


def is_public_path(path: str) -> bool:
    path = normalize(path)

    log.info(f"[AUTH DEBUG] CHECK PATH = {path}")

    # =========================
    # EXACT MATCH
    # =========================
    if path in settings.PUBLIC_PATHS:
        log.info("[AUTH DEBUG] MATCH EXACT")
        return True

    # =========================
    # PREFIX MATCH (FIXED VERSION)
    # =========================
    for prefix in settings.PUBLIC_PATH_PREFIXES:
        prefix = normalize(prefix)

        # FIX: jangan pakai startswith prefix+"/" doang
        if path == prefix or path.startswith(prefix):
            log.info(f"[AUTH DEBUG] MATCH PREFIX = {prefix}")
            return True

    # =========================
    # API AUTH BYPASS
    # =========================
    if path.startswith("/api/auth/"):
        log.info("[AUTH DEBUG] MATCH API AUTH")
        return True

    # =========================
    # DEBUG DOCS
    # =========================
    if settings.DEBUG and path.startswith(("/docs", "/redoc")):
        log.info("[AUTH DEBUG] MATCH DOCS")
        return True

    log.warning("[AUTH DEBUG] PROTECTED PATH")
    return False


def should_return_json(request: Request) -> bool:
    path = request.url.path

    if path.startswith("/api/"):
        return True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True

    accept = request.headers.get("Accept", "")
    return "application/json" in accept and "text/html" not in accept