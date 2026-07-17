"""
Portal Joki - Logout Service

Service untuk proses logout dan manajemen session joki.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.portal_joki.repositories.auth.auth_repo import PortalJokiAuthRepository
from app.utils.logger import log


# ==========================================================
# SESSION CONSTANTS
# ==========================================================
SESSION_KEY = "portal_joki"


# ==========================================================
# LOGOUT SERVICE
# ==========================================================
class PortalJokiLogoutService:
    """
    Logout Portal Joki.

    Service untuk:
    - Logout (menghapus session)
    - Cek status login
    - Mendapatkan user dari session
    - Log login activity (future)
    - Blacklist token (future)
    """

    @staticmethod
    def logout(session: Dict[str, Any]) -> bool:
        """
        Proses logout joki.
        
        Args:
            session: Session dictionary (FastAPI session)
            
        Returns:
            bool: True jika berhasil
        """
        # Log sebelum logout
        user_data = session.get(SESSION_KEY)
        if user_data:
            log.info(f"Logout: {user_data.get('kode', 'unknown')} | ID: {user_data.get('id', 'unknown')}")
        else:
            log.debug("Logout: No active session found")
        
        # Hapus session
        try:
            session.pop(SESSION_KEY, None)
            log.info("Session cleared successfully")
            return True
        except Exception as e:
            log.error(f"Failed to clear session: {e}")
            return False

    @staticmethod
    def is_logged_in(session: Dict[str, Any]) -> bool:
        """
        Cek apakah joki sedang login.
        
        Args:
            session: Session dictionary
            
        Returns:
            bool: True jika login
        """
        is_logged = SESSION_KEY in session
        log.debug(f"Check is_logged_in: {is_logged}")
        return is_logged

    @staticmethod
    def get_current_user(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan data user dari session.
        
        Args:
            session: Session dictionary
            
        Returns:
            dict: User data atau None
        """
        user_data = session.get(SESSION_KEY)
        
        if not user_data:
            log.debug("No user data in session")
            return None
        
        # Get fresh data from database
        try:
            user_id = user_data.get("id")
            if not user_id:
                log.warning("User ID not found in session")
                return None
            
            user = PortalJokiAuthRepository.get_by_id(user_id)
            
            if not user:
                log.warning(f"User not found in database: ID={user_id}")
                # Session invalid, clear it
                session.pop(SESSION_KEY, None)
                return None
            
            log.debug(f"Current user: {user.get('kode')} | ID={user_id}")
            return user
            
        except Exception as e:
            log.error(f"Failed to get current user: {e}")
            return None

    @staticmethod
    def get_current_user_light(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan data user dari session (tanpa query DB).
        
        Args:
            session: Session dictionary
            
        Returns:
            dict: User data dari session atau None
        """
        user_data = session.get(SESSION_KEY)
        
        if not user_data:
            log.debug("No user data in session (light)")
            return None
        
        log.debug(f"Current user (light): {user_data.get('kode')}")
        return user_data

    @staticmethod
    def get_user_id(session: Dict[str, Any]) -> Optional[int]:
        """
        Mendapatkan user ID dari session.
        
        Args:
            session: Session dictionary
            
        Returns:
            int: User ID atau None
        """
        user_data = session.get(SESSION_KEY)
        return user_data.get("id") if user_data else None

    @staticmethod
    def get_user_kode(session: Dict[str, Any]) -> Optional[str]:
        """
        Mendapatkan kode user dari session.
        
        Args:
            session: Session dictionary
            
        Returns:
            str: Kode user atau None
        """
        user_data = session.get(SESSION_KEY)
        return user_data.get("kode") if user_data else None

    @staticmethod
    def get_session_info(session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mendapatkan info session.
        
        Args:
            session: Session dictionary
            
        Returns:
            dict: Info session
        """
        user_data = session.get(SESSION_KEY)
        
        if not user_data:
            return {
                "authenticated": False,
                "message": "Not logged in",
            }
        
        return {
            "authenticated": True,
            "user_id": user_data.get("id"),
            "kode": user_data.get("kode"),
            "nama": user_data.get("nama"),
            "role": "joki",
            "session_key": SESSION_KEY,
        }

    @staticmethod
    def set_current_user(
        session: Dict[str, Any],
        user_data: Dict[str, Any],
    ) -> bool:
        """
        Set user data ke session (untuk login).
        
        Args:
            session: Session dictionary
            user_data: User data dari repository
            
        Returns:
            bool: True jika berhasil
        """
        if not user_data:
            log.error("Cannot set empty user data to session")
            return False
        
        try:
            # Prepare session data (remove sensitive info)
            session_data = {
                "id": user_data.get("id"),
                "kode": user_data.get("kode"),
                "nama": user_data.get("nama"),
                "no_hp": user_data.get("no_hp"),
                "login_time": datetime.now().isoformat(),
            }
            
            session[SESSION_KEY] = session_data
            log.info(f"Session set for: {session_data.get('kode')} | ID: {session_data.get('id')}")
            return True
            
        except Exception as e:
            log.error(f"Failed to set current user: {e}")
            return False

    @staticmethod
    def refresh_session(
        session: Dict[str, Any],
    ) -> bool:
        """
        Refresh session data dari database.
        
        Args:
            session: Session dictionary
            
        Returns:
            bool: True jika berhasil refresh
        """
        user_data = session.get(SESSION_KEY)
        
        if not user_data:
            log.warning("Cannot refresh: no session data")
            return False
        
        try:
            user_id = user_data.get("id")
            if not user_id:
                log.warning("Cannot refresh: no user ID")
                return False
            
            fresh_user = PortalJokiAuthRepository.get_by_id(user_id)
            
            if not fresh_user:
                log.warning(f"Refresh failed: user not found ID={user_id}")
                session.pop(SESSION_KEY, None)
                return False
            
            # Update session
            return PortalJokiLogoutService.set_current_user(session, fresh_user)
            
        except Exception as e:
            log.error(f"Failed to refresh session: {e}")
            return False

    @staticmethod
    def clear_all_sessions(session: Dict[str, Any]) -> bool:
        """
        Clear all session data (logout from all devices).
        Untuk implementasi future dengan session blacklist.
        
        Args:
            session: Session dictionary
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # For now, just clear current session
            session.clear()
            log.info("All sessions cleared")
            return True
        except Exception as e:
            log.error(f"Failed to clear all sessions: {e}")
            return False


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
logout_service = PortalJokiLogoutService()


# ==========================================================
# DEPENDENCY FOR FASTAPI
# ==========================================================
def get_current_joki(request) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency untuk mendapatkan joki dari session.
    
    Usage:
        @app.get("/profile")
        async def profile(request: Request):
            user = get_current_joki(request)
            if not user:
                return RedirectResponse("/portal-joki/login")
            return {"user": user}
    """
    from fastapi import Request
    session = request.session if hasattr(request, "session") else {}
    return PortalJokiLogoutService.get_current_user(session)


def require_joki_auth(request):
    """
    FastAPI dependency untuk memvalidasi auth joki.
    
    Usage:
        @app.get("/dashboard")
        async def dashboard(request: Request, _=Depends(require_joki_auth)):
            ...
    """
    from fastapi import Request, HTTPException
    session = request.session if hasattr(request, "session") else {}
    
    if not PortalJokiLogoutService.is_logged_in(session):
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"Location": "/portal-joki/login"},
        )
    
    user = PortalJokiLogoutService.get_current_user(session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid session",
        )
    
    return user