from fastapi import Request
from typing import Set

from app.core.config import settings

# ================================
# Precompute (biar cepat per request)
# ================================
PUBLIC_PATHS_SET: Set[str] = set(settings.PUBLIC_PATHS)
PUBLIC_EXACT_SET: Set[str] = set(settings.PUBLIC_EXACT)
PUBLIC_PREFIXES = settings.PUBLIC_PATH_PREFIXES


def is_public_path(path: str) -> bool:
    path = (path or "").rstrip("/") or "/"

    print("[AUTH DEBUG] PATH =", path)
    print("[AUTH DEBUG] PREFIXES =", settings.PUBLIC_PATH_PREFIXES)

    # EXACT
    if path in settings.PUBLIC_PATHS:
        return True

    # PREFIX
    for prefix in settings.PUBLIC_PATH_PREFIXES:
        prefix = prefix.rstrip("/")
        if path == prefix or path.startswith(prefix + "/"):
            return True

    # API bypass
    if path.startswith("/api/auth/"):
        return True

    # docs debug
    if settings.DEBUG and path.startswith(("/docs", "/redoc")):
        return True

    return False

    
# ================================
# Response Type Detector
# ================================
def should_return_json(request: Request) -> bool:
    """Determine if response should be JSON or redirect"""

    path = request.url.path

    # API langsung JSON
    if path.startswith("/api/"):
        return True

    # AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True

    # Accept header
    accept = request.headers.get("Accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return True

    return False
