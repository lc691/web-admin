"""
Portal Joki - Login Service

Service untuk proses login, logout, dan manajemen password joki.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from passlib.context import CryptContext

from app.portal_joki.repositories.auth.auth_repo import PortalJokiAuthRepository
from app.utils.logger import log

# ==========================================================
# PASSWORD CONTEXT
# ==========================================================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ==========================================================
# RESULT CLASS
# ==========================================================
class LoginResult:
    """
    Result object untuk proses login.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        user: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.user = user
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "user": self.user,
            "data": self.data,
        }
    
    @classmethod
    def success(cls, message: str, user: Dict[str, Any]) -> "LoginResult":
        """Create success result."""
        return cls(True, message, user)
    
    @classmethod
    def error(cls, message: str) -> "LoginResult":
        """Create error result."""
        return cls(False, message)


# ==========================================================
# LOGIN SERVICE
# ==========================================================
class PortalJokiLoginService:
    """
    Service Login Portal Joki.

    Business Flow:
    1. Cek kode joki
    2. Cek aktif
    3. Cek password
    4. Update last_login
    5. Return user
    """

    @staticmethod
    def login(
        kode: str,
        password: str,
        ip_address: Optional[str] = None,
    ) -> LoginResult:
        """
        Proses login joki.
        
        Args:
            kode: Kode login joki
            password: Password plain text
            ip_address: IP address (untuk logging)
            
        Returns:
            LoginResult: Hasil login
        """
        kode = kode.strip().upper()
        log.info(f"Login attempt: {kode} | IP: {ip_address or 'unknown'}")

        # ==========================================================
        # 1. Cari Joki
        # ==========================================================
        user = PortalJokiAuthRepository.get_by_kode(kode)

        if not user:
            log.warning(f"Login failed: kode not found - {kode}")
            return LoginResult.error("Kode joki tidak ditemukan.")

        # ==========================================================
        # 2. Status Aktif
        # ==========================================================
        if not user.get("aktif", False):
            log.warning(f"Login failed: inactive user - {kode}")
            return LoginResult.error("Joki sudah dinonaktifkan. Hubungi admin.")

        # ==========================================================
        # 3. Password Validation
        # ==========================================================
        if not user.get("password_hash"):
            log.warning(f"Login failed: no password set - {kode}")
            return LoginResult.error("Password belum dibuat. Hubungi admin.")

        # ==========================================================
        # 4. Verifikasi Password
        # ==========================================================
        try:
            password_valid = pwd_context.verify(
                password,
                user["password_hash"],
            )
        except Exception as e:
            log.error(f"Password verification error for {kode}: {e}")
            return LoginResult.error("Terjadi kesalahan verifikasi password.")

        if not password_valid:
            log.warning(f"Login failed: wrong password - {kode}")
            return LoginResult.error("Password salah.")

        # ==========================================================
        # 5. Update Last Login
        # ==========================================================
        try:
            PortalJokiAuthRepository.update_last_login(user["id"])
            log.info(f"Updated last_login for: {kode}")
        except Exception as e:
            log.error(f"Failed to update last_login for {kode}: {e}")
            # Non-critical, continue

        # ==========================================================
        # 6. Refresh Data
        # ==========================================================
        user = PortalJokiAuthRepository.get_by_id(user["id"])

        # Remove sensitive data for return
        if user and "password_hash" in user:
            user_copy = user.copy()
            user_copy.pop("password_hash", None)
        else:
            user_copy = user

        log.info(f"Login successful: {kode} | ID: {user['id']}")
        
        return LoginResult.success(
            "Login berhasil.",
            user_copy,
        )

    @staticmethod
    def change_password(
        joki_id: int,
        password_baru: str,
        old_password: Optional[str] = None,
    ) -> LoginResult:
        """
        Change password for joki.
        
        Args:
            joki_id: ID joki
            password_baru: Password baru
            old_password: Password lama (opsional, untuk verifikasi)
            
        Returns:
            LoginResult: Hasil perubahan password
        """
        log.info(f"Change password attempt for joki_id: {joki_id}")
        
        # ==========================================================
        # 1. Validate user exists
        # ==========================================================
        user = PortalJokiAuthRepository.get_by_id(joki_id)
        
        if not user:
            log.warning(f"Change password failed: user not found - {joki_id}")
            return LoginResult.error("Joki tidak ditemukan.")

        # ==========================================================
        # 2. Verify old password if provided
        # ==========================================================
        if old_password is not None:
            if not user.get("password_hash"):
                return LoginResult.error("Password belum dibuat.")
            
            if not pwd_context.verify(old_password, user["password_hash"]):
                log.warning(f"Change password failed: wrong old password - {joki_id}")
                return LoginResult.error("Password lama salah.")

        # ==========================================================
        # 3. Validate new password
        # ==========================================================
        password_validation = PortalJokiLoginService.validate_password(password_baru)
        if not password_validation["valid"]:
            return LoginResult.error(password_validation["message"])

        # ==========================================================
        # 4. Update password
        # ==========================================================
        try:
            password_hash = PortalJokiLoginService.hash_password(password_baru)
            PortalJokiAuthRepository.update_password(joki_id, password_hash)
            
            log.info(f"Password changed successfully for joki_id: {joki_id}")
            return LoginResult.success("Password berhasil diubah.", None)
            
        except Exception as e:
            log.error(f"Failed to change password for joki_id {joki_id}: {e}")
            return LoginResult.error("Gagal mengubah password.")

    @staticmethod
    def verify_password(
        plain_password: str,
        password_hash: str,
    ) -> bool:
        """
        Verify plain password against hash.
        
        Args:
            plain_password: Password plain text
            password_hash: Password hash
            
        Returns:
            bool: True jika valid
        """
        try:
            return pwd_context.verify(plain_password, password_hash)
        except Exception as e:
            log.error(f"Password verification error: {e}")
            return False

    @staticmethod
    def hash_password(
        password: str,
    ) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Password plain text
            
        Returns:
            str: Password hash
        """
        return pwd_context.hash(password)

    @staticmethod
    def validate_password(
        password: str,
        min_length: int = 8,
    ) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            min_length: Minimum length
            
        Returns:
            dict: Validation result
        """
        errors = []
        
        if len(password) < min_length:
            errors.append(f"Password minimal {min_length} karakter.")
        
        if not any(c.isupper() for c in password):
            errors.append("Password harus mengandung huruf kapital.")
        
        if not any(c.islower() for c in password):
            errors.append("Password harus mengandung huruf kecil.")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password harus mengandung angka.")
        
        # Cek common passwords
        common_passwords = {
            "password", "12345678", "qwerty123", "admin123",
            "password123", "123456789", "admin", "root",
            "joki123", "abcdefgh", "11111111", "test1234"
        }
        
        if password.lower() in common_passwords:
            errors.append("Password terlalu umum/lemah.")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "message": "Password valid." if len(errors) == 0 else " ".join(errors),
        }

    @staticmethod
    def reset_password(
        joki_id: int,
        new_password: Optional[str] = None,
    ) -> LoginResult:
        """
        Reset password (admin function).
        
        Args:
            joki_id: ID joki
            new_password: Password baru (opsional, akan generate jika None)
            
        Returns:
            LoginResult: Hasil reset password
        """
        import secrets
        import string
        
        log.info(f"Reset password attempt for joki_id: {joki_id}")
        
        # ==========================================================
        # 1. Validate user exists
        # ==========================================================
        user = PortalJokiAuthRepository.get_by_id(joki_id)
        
        if not user:
            log.warning(f"Reset password failed: user not found - {joki_id}")
            return LoginResult.error("Joki tidak ditemukan.")

        # ==========================================================
        # 2. Generate or use provided password
        # ==========================================================
        if new_password is None:
            # Generate random password: 12 chars with upper, lower, digits
            alphabet = string.ascii_letters + string.digits
            new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Validate password (if provided manually)
        if new_password:
            validation = PortalJokiLoginService.validate_password(new_password)
            if not validation["valid"]:
                return LoginResult.error(validation["message"])

        # ==========================================================
        # 3. Update password
        # ==========================================================
        try:
            password_hash = PortalJokiLoginService.hash_password(new_password)
            PortalJokiAuthRepository.update_password(joki_id, password_hash)
            
            log.info(f"Password reset successfully for joki_id: {joki_id}")
            
            return LoginResult.success(
                f"Password berhasil direset. Password baru: {new_password}",
                {"new_password": new_password},
            )
            
        except Exception as e:
            log.error(f"Failed to reset password for joki_id {joki_id}: {e}")
            return LoginResult.error("Gagal mereset password.")

    @staticmethod
    def get_joki_session_data(user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare session data for authenticated joki.
        
        Args:
            user: User data from repository
            
        Returns:
            dict: Session data (without password hash)
        """
        if not user:
            return {}
        
        return {
            "id": user.get("id"),
            "kode": user.get("kode"),
            "nama": user.get("nama"),
            "no_hp": user.get("no_hp"),
            "role": "joki",
            "login_time": datetime.now().isoformat(),
        }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
login_service = PortalJokiLoginService()