"""
Middleware Configuration untuk SoundON Admin Dashboard
"""

from time import time
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from itsdangerous import BadSignature

from app.core.auth import read_session
from app.core.policy_loader import get_policy
from app.core.config import settings
from app.utils.logger import log


def setup_middleware(app: FastAPI):
    """
    Setup semua middleware untuk aplikasi FastAPI.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        FastAPI: App dengan middleware terpasang
    """
    # Auth middleware (selalu dipasang)
    app.middleware("http")(auth_middleware)
    
    log.info("✅ Middleware setup completed")
    return app


async def auth_middleware(request: Request, call_next):
    """
    Middleware untuk autentikasi dan otorisasi.
    
    - Mengecek apakah path public
    - Validasi session cookie
    - Menambahkan user info ke request.state
    """
    start = time()
    path = request.url.path
    
    # ================================
    # 1. POLICY CHECK (FAST PATH)
    # ================================
    policy = get_policy()
    is_public = policy.is_public(path)
    
    log.debug(f"[REQ] path={path} public={is_public} method={request.method}")
    
    if is_public:
        return await call_next(request)
    
    # ================================
    # 2. AUTH CHECK (API & WEB)
    # ================================
    token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    
    if not token:
        log.warning(f"[AUTH] No token found for path={path}")
        return await handle_unauthorized(request, path)
    
    try:
        user = read_session(token)
        
        if not user or not user.get("username"):
            raise ValueError("Invalid session data")
        
        # Set user data ke request state
        request.state.user = user
        request.state.user_id = user.get("user_id")
        request.state.username = user.get("username")
        request.state.is_authenticated = True
        request.state.session_token = token
        
        log.debug(f"[AUTH] User authenticated: {user.get('username')}")
        
    except BadSignature:
        log.warning(f"[AUTH] Invalid signature for path={path}")
        return await handle_unauthorized(request, path)
        
    except Exception as e:
        log.error(f"[AUTH] Error: {e} for path={path}", exc_info=True)
        return await handle_unauthorized(request, path)
    
    # ================================
    # 3. PROCESS REQUEST
    # ================================
    response = await call_next(request)
    
    # ================================
    # 4. LOGGING
    # ================================
    duration = round((time() - start) * 1000, 2)
    log.info(f"[REQ DONE] path={path} ms={duration} status={response.status_code}")
    
    return response


async def handle_unauthorized(request: Request, path: str):
    """
    Handler untuk unauthorized requests.
    
    - API requests: return JSON 401
    - Web requests: redirect ke login
    """
    # Cek apakah request dari API (biasanya /api/*)
    if path.startswith("/api/"):
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "Unauthorized. Please login first.",
                "code": "UNAUTHORIZED"
            }
        )
    
    # Web request - redirect ke login
    return RedirectResponse(
        url="/login",
        status_code=303,
        headers={"Cache-Control": "no-cache"}
    )


# ================================
# MIDDLEWARE UTILITY FUNCTIONS
# ================================
def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from request state"""
    return getattr(request.state, "user", None)


def get_user_id(request: Request) -> Optional[int]:
    """Get current user ID from request state"""
    return getattr(request.state, "user_id", None)


def get_username(request: Request) -> Optional[str]:
    """Get current username from request state"""
    return getattr(request.state, "username", None)


def is_authenticated(request: Request) -> bool:
    """Check if request is authenticated"""
    return getattr(request.state, "is_authenticated", False)


# ================================
# CORS MIDDLEWARE
# ================================
def setup_cors_middleware(app: FastAPI):
    """Setup CORS middleware (opsional)"""
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    log.info("✅ CORS middleware configured")
    return app