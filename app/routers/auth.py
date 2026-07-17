"""
Authentication Routes - Login, Logout, Session Management
"""

from datetime import datetime
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from app.core.auth import create_session, verify_password, read_session
from app.core.config import settings
from app.templates import templates
from app.utils.logger import log

router = APIRouter(tags=["authentication"])


# ================================
# CONSTANTS
# ================================
SESSION_COOKIE_NAME = settings.AUTH_COOKIE_NAME
SESSION_MAX_AGE = settings.AUTH_COOKIE_MAX_AGE


# ================================
# HELPERS
# ================================
def authenticate_admin(username: str, password: str) -> bool:
    """
    Authenticate admin user.
    
    Args:
        username: Admin username
        password: Admin password (plain text)
        
    Returns:
        bool: True if authenticated
    """
    return username == settings.ADMIN_USERNAME and verify_password(
        password, settings.ADMIN_PASSWORD_HASH
    )


def set_auth_cookie(response: Response, token: str, remember: bool = False):
    """
    Set authentication cookie.
    
    Args:
        response: FastAPI Response object
        token: Session token
        remember: If True, cookie will persist (7 days)
    """
    max_age = 60 * 60 * 24 * 7 if remember else None  # 7 days if remember

    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        max_age=max_age,
        path="/",
    )


def clear_auth_cookie(response: Response):
    """
    Clear authentication cookie.
    
    Args:
        response: FastAPI Response object
    """
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


def get_session_user(token: str) -> dict:
    """
    Get user data from session token.
    
    Args:
        token: Session token
        
    Returns:
        dict: User data or empty dict if invalid
    """
    try:
        return read_session(token)
    except Exception as e:
        log.debug(f"Invalid session: {e}")
        return {}


# ================================
# LOGIN PAGE
# ================================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Display login page.
    Redirect to dashboard if already authenticated.
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)

    if token:
        try:
            user = read_session(token)
            if user:
                log.debug(f"User already logged in: {user.get('username')}")
                return RedirectResponse("/", status_code=303)
        except Exception as e:
            log.debug(f"Invalid session: {e}")

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": request.query_params.get("error"),
            "message": request.query_params.get("message"),
            "next": request.query_params.get("next", "/"),
        },
    )


# ================================
# LOGIN ACTION
# ================================
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    """
    Process login form submission.
    """
    client_ip = request.client.host if request.client else "unknown"
    log.info(f"Login attempt: {username} | IP: {client_ip}")

    # Authenticate
    if not authenticate_admin(username, password):
        log.warning(f"Login failed: {username} | IP: {client_ip}")
        
        # AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "detail": "Invalid username or password"
                },
            )
        
        # Web request
        return RedirectResponse(
            "/login?error=Invalid credentials",
            status_code=303,
        )

    # Create session
    session_data = {
        "user_id": 1,
        "username": username,
        "role": "admin",
        "login_time": datetime.now().isoformat(),
        "ip_address": client_ip,
    }

    token = create_session(session_data)
    
    # Redirect to dashboard
    resp = RedirectResponse("/", status_code=303)
    set_auth_cookie(resp, token, remember)

    log.info(f"Login success: {username} | IP: {client_ip} | Remember: {remember}")
    return resp


# ================================
# LOGOUT
# ================================
@router.get("/logout")
async def logout(request: Request):
    """
    Logout user and clear session.
    """
    client_ip = request.client.host if request.client else "unknown"
    username = "unknown"

    # Get user info before clearing session
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        user = get_session_user(token)
        username = user.get("username", "unknown")

    log.info(f"Logout: {username} | IP: {client_ip}")

    # Redirect with message
    resp = RedirectResponse(
        "/login?message=Logged out successfully",
        status_code=303,
    )
    clear_auth_cookie(resp)

    return resp


# ================================
# SESSION CHECK (AJAX)
# ================================
@router.get("/api/auth/me")
async def get_current_user(request: Request):
    """
    Get current authenticated user (for AJAX/API calls).
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not token:
        return JSONResponse(
            status_code=401,
            content={"authenticated": False, "message": "Not authenticated"},
        )
    
    user = get_session_user(token)
    
    if not user:
        return JSONResponse(
            status_code=401,
            content={"authenticated": False, "message": "Invalid session"},
        )
    
    return JSONResponse(
        content={
            "authenticated": True,
            "user": {
                "id": user.get("user_id"),
                "username": user.get("username"),
                "role": user.get("role", "admin"),
            }
        }
    )


# ================================
# UNAUTHORIZED PAGE
# ================================
@router.get("/unauthorized", response_class=HTMLResponse)
async def unauthorized_page(request: Request):
    """
    Display unauthorized access page.
    """
    return templates.TemplateResponse(
        "unauthorized.html",
        {
            "request": request,
            "message": request.query_params.get("message", "You don't have permission to access this page."),
        },
        status_code=403,
    )


# ================================
# SESSION REFRESH (Optional)
# ================================
@router.post("/api/auth/refresh")
async def refresh_session(request: Request, response: Response):
    """
    Refresh session token (extend expiration).
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not token:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "No session"},
        )
    
    try:
        user = read_session(token)
        if not user:
            raise ValueError("Invalid session")
        
        # Create new token with extended expiration
        new_token = create_session(user)
        
        # Set new cookie
        response.set_cookie(
            SESSION_COOKIE_NAME,
            new_token,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            secure=settings.AUTH_COOKIE_SECURE,
            max_age=SESSION_MAX_AGE,
            path="/",
        )
        
        return JSONResponse(
            content={"success": True, "message": "Session refreshed"}
        )
        
    except Exception as e:
        log.error(f"Session refresh failed: {e}")
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid session"},
        )