"""
Authentication utilities untuk session management dan password handling
"""

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import hashlib
import bcrypt

from app.core.config import settings
from app.utils.logger import log

# ================================
# Serializer (singleton)
# ================================
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


# ================================
# Session Handling
# ================================
def create_session(user_data: Dict[str, Any], expires_in: Optional[int] = None) -> str:
    """
    Create signed session token.
    
    Args:
        user_data: Dictionary data user
        expires_in: Expiry time in seconds (default from settings)
        
    Returns:
        str: Encrypted session token
    """
    expires_in = expires_in or settings.AUTH_COOKIE_MAX_AGE

    payload = {
        **user_data,
        "exp": datetime.now(timezone.utc).timestamp() + expires_in,
    }

    token = serializer.dumps(payload)
    log.debug(f"✅ Session created for user: {user_data.get('username', 'unknown')}")
    return token


def read_session(token: str) -> Dict[str, Any]:
    """
    Validate and decode session token.
    
    Args:
        token: Session token dari cookie
        
    Returns:
        Dict: Session data
        
    Raises:
        BadSignature: Jika token invalid atau expired
    """
    try:
        data = serializer.loads(token, max_age=settings.AUTH_COOKIE_MAX_AGE)
    except SignatureExpired:
        log.warning("⚠️ Session expired")
        raise BadSignature("Token expired")
    except BadSignature:
        log.warning("⚠️ Invalid session signature")
        raise

    # Double check expiration (defensive)
    exp = data.get("exp")
    if exp and exp < datetime.now(timezone.utc).timestamp():
        log.warning("⚠️ Session expired (defensive check)")
        raise BadSignature("Token expired")

    return data


def destroy_session(token: str) -> bool:
    """
    Destroy/invalidate session.
    
    Args:
        token: Session token
        
    Returns:
        bool: True jika berhasil
    """
    try:
        # Coba read dulu untuk validasi
        read_session(token)
        log.debug("✅ Session destroyed")
        return True
    except BadSignature:
        # Token sudah invalid, tetap return True
        return True
    except Exception as e:
        log.error(f"❌ Error destroying session: {e}")
        return False


def get_user_from_session(token: str) -> Optional[Dict[str, Any]]:
    """
    Get user data from session.
    
    Args:
        token: Session token
        
    Returns:
        Dict: User data atau None
    """
    try:
        return read_session(token)
    except BadSignature:
        return None
    except Exception as e:
        log.error(f"❌ Error getting user from session: {e}")
        return None


# ================================
# Password Handling
# ================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password dengan support bcrypt dan legacy MD5.
    
    Args:
        plain_password: Password plain text
        hashed_password: Password hash yang tersimpan
        
    Returns:
        bool: True jika password valid
    """
    if not plain_password or not hashed_password:
        return False

    # Bcrypt (format: $2b$, $2a$, $2y$)
    if hashed_password.startswith("$2"):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception as e:
            log.error(f"❌ Bcrypt verification error: {e}")
            return False

    # Legacy MD5 fallback
    return hashlib.md5(plain_password.encode()).hexdigest() == hashed_password


def hash_password(password: str, use_bcrypt: bool = True) -> str:
    """
    Hash password dengan bcrypt atau legacy MD5.
    
    Args:
        password: Password plain text
        use_bcrypt: True untuk bcrypt, False untuk MD5
        
    Returns:
        str: Password hash
    """
    if not password:
        raise ValueError("Password cannot be empty")

    if use_bcrypt:
        try:
            hashed = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt(rounds=12)  # 12 rounds = secure & fast enough
            ).decode("utf-8")
            log.debug("✅ Password hashed with bcrypt")
            return hashed
        except Exception as e:
            log.error(f"❌ Bcrypt hashing error: {e}")
            raise

    # Legacy MD5
    log.warning("⚠️ Using legacy MD5 hashing (not recommended)")
    return hashlib.md5(password.encode()).hexdigest()


def is_password_weak(password: str) -> bool:
    """
    Cek apakah password lemah.
    
    Args:
        password: Password plain text
        
    Returns:
        bool: True jika password lemah
    """
    if len(password) < 8:
        return True
    
    # Cek common patterns
    common_passwords = {
        "password", "12345678", "qwerty123", "admin123",
        "password123", "123456789", "admin", "root"
    }
    
    if password.lower() in common_passwords:
        return True
    
    return False


# ================================
# Request Helpers
# ================================
def get_current_user(request) -> Optional[Dict[str, Any]]:
    """
    Get current user dari request state.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Dict: User data atau None
    """
    return getattr(request.state, "user", None)


def get_current_user_id(request) -> Optional[int]:
    """
    Get current user ID dari request state.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        int: User ID atau None
    """
    user = get_current_user(request)
    return user.get("user_id") if user else None


def get_current_username(request) -> Optional[str]:
    """
    Get current username dari request state.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        str: Username atau None
    """
    user = get_current_user(request)
    return user.get("username") if user else None


def is_authenticated(request) -> bool:
    """
    Cek apakah request sudah terautentikasi.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        bool: True jika authenticated
    """
    return get_current_user(request) is not None


def is_admin(request) -> bool:
    """
    Cek apakah user adalah admin.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        bool: True jika admin
    """
    user = get_current_user(request)
    if not user:
        return False
    
    user_id = user.get("user_id")
    if user_id and user_id in settings.admin_ids_list:
        return True
    
    username = user.get("username")
    return username == settings.ADMIN_USERNAME


# ================================
# Session Decorator (Optional)
# ================================
def require_auth(func):
    """
    Decorator untuk endpoint yang membutuhkan autentikasi.
    
    Usage:
        @app.get("/protected")
        @require_auth
        async def protected_endpoint(request: Request):
            user = get_current_user(request)
            return {"user": user}
    """
    from functools import wraps
    from fastapi import Request, HTTPException
    
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not is_authenticated(request):
            raise HTTPException(status_code=401, detail="Authentication required")
        return await func(request, *args, **kwargs)
    return wrapper


def require_admin(func):
    """
    Decorator untuk endpoint yang membutuhkan admin.
    
    Usage:
        @app.get("/admin-only")
        @require_admin
        async def admin_endpoint(request: Request):
            return {"message": "Admin only"}
    """
    from functools import wraps
    from fastapi import Request, HTTPException
    
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not is_authenticated(request):
            raise HTTPException(status_code=401, detail="Authentication required")
        if not is_admin(request):
            raise HTTPException(status_code=403, detail="Admin access required")
        return await func(request, *args, **kwargs)
    return wrapper


# ================================
# Utility Functions
# ================================
def generate_session_token(user_id: int, username: str, extra_data: dict = None) -> str:
    """
    Generate session token dengan data standar.
    
    Args:
        user_id: User ID
        username: Username
        extra_data: Data tambahan
        
    Returns:
        str: Session token
    """
    session_data = {
        "user_id": user_id,
        "username": username,
        **(extra_data or {})
    }
    return create_session(session_data)


# ================================
# Legacy MD5 Support (untuk migrasi)
# ================================
def migrate_password_to_bcrypt(plain_password: str, md5_hash: str) -> str:
    """
    Migrasi password dari MD5 ke bcrypt.
    
    Args:
        plain_password: Password plain text
        md5_hash: MD5 hash yang tersimpan
        
    Returns:
        str: Bcrypt hash baru jika valid
    """
    # Verifikasi MD5 dulu
    if hashlib.md5(plain_password.encode()).hexdigest() == md5_hash:
        # Hash ulang dengan bcrypt
        return hash_password(plain_password, use_bcrypt=True)
    return None