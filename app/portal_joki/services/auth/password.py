"""
Portal Joki - Password Service

Service untuk manajemen password joki.
"""

from typing import Dict, Any, Optional
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
# PASSWORD SERVICE
# ==========================================================
class PortalJokiPasswordService:
    """
    Service Password Portal Joki.
    
    Menyediakan fungsi untuk:
    - Verifikasi password
    - Hash password
    - Change password
    - Validate password strength
    - Reset password (admin)
    """

    @staticmethod
    def verify(
        plain_password: str,
        password_hash: str,
    ) -> bool:
        """
        Verifikasi password plain text terhadap hash.
        
        Args:
            plain_password: Password plain text
            password_hash: Password hash
            
        Returns:
            bool: True jika valid
        """
        try:
            result = pwd_context.verify(plain_password, password_hash)
            log.debug(f"Password verification: {'success' if result else 'failed'}")
            return result
        except Exception as e:
            log.error(f"Password verification error: {e}")
            return False

    @staticmethod
    def hash(password: str) -> str:
        """
        Hash password menggunakan bcrypt.
        
        Args:
            password: Password plain text
            
        Returns:
            str: Password hash
        """
        try:
            hashed = pwd_context.hash(password)
            log.debug("Password hashed successfully")
            return hashed
        except Exception as e:
            log.error(f"Password hashing error: {e}")
            raise

    @staticmethod
    def change(
        joki_id: int,
        password_baru: str,
        password_lama: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Change password joki.
        
        Args:
            joki_id: ID joki
            password_baru: Password baru
            password_lama: Password lama (opsional, untuk verifikasi)
            
        Returns:
            dict: Result dengan status dan message
        """
        log.info(f"Password change attempt for joki_id: {joki_id}")
        
        # ==========================================================
        # 1. Validate user exists
        # ==========================================================
        user = PortalJokiAuthRepository.get_by_id(joki_id)
        
        if not user:
            log.warning(f"Password change failed: user not found - {joki_id}")
            return {
                "success": False,
                "message": "Joki tidak ditemukan.",
            }

        # ==========================================================
        # 2. Verify old password if provided
        # ==========================================================
        if password_lama is not None:
            if not user.get("password_hash"):
                log.warning(f"Password change failed: no password set - {joki_id}")
                return {
                    "success": False,
                    "message": "Password belum dibuat. Hubungi admin.",
                }
            
            if not PortalJokiPasswordService.verify(password_lama, user["password_hash"]):
                log.warning(f"Password change failed: wrong old password - {joki_id}")
                return {
                    "success": False,
                    "message": "Password lama salah.",
                }

        # ==========================================================
        # 3. Validate new password
        # ==========================================================
        password_validation = PortalJokiPasswordService.validate(password_baru)
        if not password_validation["valid"]:
            log.warning(f"Password change failed: invalid password - {joki_id}")
            return {
                "success": False,
                "message": password_validation["message"],
                "errors": password_validation["errors"],
            }

        # ==========================================================
        # 4. Update password
        # ==========================================================
        try:
            password_hash = PortalJokiPasswordService.hash(password_baru)
            success = PortalJokiAuthRepository.update_password(joki_id, password_hash)
            
            if success:
                log.info(f"Password changed successfully for joki_id: {joki_id}")
                return {
                    "success": True,
                    "message": "Password berhasil diubah.",
                }
            else:
                log.error(f"Password change failed: DB update error - {joki_id}")
                return {
                    "success": False,
                    "message": "Gagal mengubah password. Silakan coba lagi.",
                }
                
        except Exception as e:
            log.error(f"Password change exception for joki_id {joki_id}: {e}")
            return {
                "success": False,
                "message": f"Terjadi kesalahan: {str(e)}",
            }

    @staticmethod
    def validate(
        password: str,
        min_length: int = 8,
        require_upper: bool = True,
        require_lower: bool = True,
        require_digit: bool = True,
        require_special: bool = False,
    ) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            min_length: Minimum length
            require_upper: Require uppercase letter
            require_lower: Require lowercase letter
            require_digit: Require digit
            require_special: Require special character
            
        Returns:
            dict: Validation result
        """
        errors = []
        
        # Length check
        if len(password) < min_length:
            errors.append(f"Password minimal {min_length} karakter.")
        
        # Uppercase check
        if require_upper and not any(c.isupper() for c in password):
            errors.append("Password harus mengandung huruf kapital (A-Z).")
        
        # Lowercase check
        if require_lower and not any(c.islower() for c in password):
            errors.append("Password harus mengandung huruf kecil (a-z).")
        
        # Digit check
        if require_digit and not any(c.isdigit() for c in password):
            errors.append("Password harus mengandung angka (0-9).")
        
        # Special character check
        if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password harus mengandung karakter spesial (!@#$%^&*).")
        
        # Common passwords check
        common_passwords = {
            "password", "12345678", "qwerty123", "admin123",
            "password123", "123456789", "admin", "root",
            "joki123", "abcdefgh", "11111111", "test1234",
            "1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm",
            "jokipassword", "jokijoki", "12345", "abc123",
        }
        
        if password.lower() in common_passwords:
            errors.append("Password terlalu umum/lemah. Gunakan kombinasi yang lebih unik.")
        
        # Check if password contains username-like patterns
        if password.isalpha():
            errors.append("Password harus mengandung angka atau karakter spesial.")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "message": "Password valid." if len(errors) == 0 else " ".join(errors),
            "strength": "weak" if len(errors) > 2 else "medium" if len(errors) > 0 else "strong",
        }

    @staticmethod
    def reset(
        joki_id: int,
        new_password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reset password (admin function).
        
        Args:
            joki_id: ID joki
            new_password: Password baru (opsional, akan generate jika None)
            
        Returns:
            dict: Result dengan status, message, dan new_password
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
            return {
                "success": False,
                "message": "Joki tidak ditemukan.",
            }

        # ==========================================================
        # 2. Generate or use provided password
        # ==========================================================
        generated = False
        
        if new_password is None:
            # Generate random password: 10 chars with upper, lower, digits
            alphabet = string.ascii_letters + string.digits
            new_password = ''.join(secrets.choice(alphabet) for _ in range(10))
            generated = True
        
        # Validate password (if provided manually)
        if new_password:
            validation = PortalJokiPasswordService.validate(new_password)
            if not validation["valid"]:
                log.warning(f"Reset password failed: invalid password - {joki_id}")
                return {
                    "success": False,
                    "message": validation["message"],
                    "errors": validation["errors"],
                }

        # ==========================================================
        # 3. Update password
        # ==========================================================
        try:
            password_hash = PortalJokiPasswordService.hash(new_password)
            success = PortalJokiAuthRepository.update_password(joki_id, password_hash)
            
            if success:
                log.info(f"Password reset successfully for joki_id: {joki_id}")
                return {
                    "success": True,
                    "message": f"Password berhasil direset.",
                    "new_password": new_password if generated else None,
                    "generated": generated,
                    "user": {
                        "id": user.get("id"),
                        "kode": user.get("kode"),
                        "nama": user.get("nama"),
                    }
                }
            else:
                log.error(f"Password reset failed: DB update error - {joki_id}")
                return {
                    "success": False,
                    "message": "Gagal mereset password. Silakan coba lagi.",
                }
                
        except Exception as e:
            log.error(f"Password reset exception for joki_id {joki_id}: {e}")
            return {
                "success": False,
                "message": f"Terjadi kesalahan: {str(e)}",
            }

    @staticmethod
    def has_password(joki_id: int) -> bool:
        """
        Cek apakah joki sudah memiliki password.
        
        Args:
            joki_id: ID joki
            
        Returns:
            bool: True jika sudah memiliki password
        """
        try:
            user = PortalJokiAuthRepository.get_by_id(joki_id)
            return bool(user and user.get("password_hash"))
        except Exception as e:
            log.error(f"Error checking password for joki_id {joki_id}: {e}")
            return False

    @staticmethod
    def verify_plain(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """
        Alias untuk verify.
        
        Args:
            plain_password: Password plain text
            hashed_password: Password hash
            
        Returns:
            bool: True jika valid
        """
        return PortalJokiPasswordService.verify(plain_password, hashed_password)

    @staticmethod
    def generate_strong_password(length: int = 10) -> str:
        """
        Generate strong random password.
        
        Args:
            length: Panjang password (default 10)
            
        Returns:
            str: Random password
        """
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        log.debug(f"Generated strong password: {'*' * length}")
        return password


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
password_service = PortalJokiPasswordService()