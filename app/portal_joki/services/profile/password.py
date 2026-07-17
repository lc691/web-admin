"""
Portal Joki - Password Service (Profile)

Service untuk manajemen password joki dari profile.
"""

from typing import Optional, Dict, Any, List
import re
import secrets
import string

from app.core.security import (
    hash_password,
    verify_password,
)
from app.portal_joki.repositories.profile.profile_repo import (
    PortalJokiProfileRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class PasswordResult:
    """
    Result object untuk operasi password.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.errors = errors or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
        }
    
    @classmethod
    def ok(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "PasswordResult":
        """Create success result."""
        return cls(True, message, data or {})
    
    @classmethod
    def error(
        cls,
        message: str,
        errors: Optional[List[str]] = None,
    ) -> "PasswordResult":
        """Create error result."""
        return cls(False, message, {}, errors or [])


# ==========================================================
# PASSWORD SERVICE
# ==========================================================
class PortalJokiPasswordService:
    """
    Service Password Portal Joki (Profile).
    
    Menyediakan fungsi untuk:
    - Change password (dengan verifikasi old password)
    - Reset password (admin)
    - Validate password strength
    - Generate strong password
    """

    @staticmethod
    def change(
        *,
        profile: Dict[str, Any],
        old_password: str,
        new_password: str,
        confirm_password: str,
    ) -> PasswordResult:
        """
        Change password with old password verification.
        
        Args:
            profile: Profile data (must include id, password_hash)
            old_password: Password lama
            new_password: Password baru
            confirm_password: Konfirmasi password baru
            
        Returns:
            PasswordResult: Result status
        """
        joki_id = profile.get("id")
        log.info(f"Change password attempt: joki_id={joki_id}")
        
        # ==========================================================
        # 1. VALIDASI PASSWORD LAMA
        # ==========================================================
        password_hash = profile.get("password_hash")
        
        if not password_hash:
            log.warning(f"No password set: joki_id={joki_id}")
            return PasswordResult.error("Password belum dibuat. Hubungi admin.")
        
        try:
            if not verify_password(old_password, password_hash):
                log.warning(f"Wrong old password: joki_id={joki_id}")
                return PasswordResult.error("Password lama salah.")
        except Exception as e:
            log.error(f"Failed to verify password: {e}")
            return PasswordResult.error(f"Gagal verifikasi password: {str(e)}")
        
        # ==========================================================
        # 2. VALIDASI PASSWORD BARU
        # ==========================================================
        validation = PortalJokiPasswordService.validate_password(new_password)
        if not validation["valid"]:
            log.warning(f"Invalid new password: joki_id={joki_id}")
            return PasswordResult.error(
                validation["message"],
                validation["errors"],
            )
        
        # ==========================================================
        # 3. VALIDASI KONFIRMASI
        # ==========================================================
        if new_password != confirm_password:
            log.warning(f"Password mismatch: joki_id={joki_id}")
            return PasswordResult.error("Konfirmasi password tidak sama.")
        
        # ==========================================================
        # 4. CEK PASSWORD SAMA
        # ==========================================================
        try:
            if verify_password(new_password, password_hash):
                log.warning(f"New password same as old: joki_id={joki_id}")
                return PasswordResult.error("Password baru tidak boleh sama dengan password lama.")
        except Exception:
            pass  # Skip if verification fails
        
        # ==========================================================
        # 5. UPDATE PASSWORD
        # ==========================================================
        try:
            new_password_hash = hash_password(new_password)
            success = PortalJokiProfileRepository.update_password(
                joki_id,
                new_password_hash,
            )
            
            if not success:
                log.error(f"Failed to update password: joki_id={joki_id}")
                return PasswordResult.error("Gagal memperbarui password.")
            
            log.info(f"Password changed successfully: joki_id={joki_id}")
            
            return PasswordResult.ok(
                "Password berhasil diperbarui.",
                {"joki_id": joki_id},
            )
            
        except Exception as e:
            log.error(f"Failed to change password: {e}")
            return PasswordResult.error(f"Gagal memperbarui password: {str(e)}")

    @staticmethod
    def reset(
        joki_id: int,
        new_password: Optional[str] = None,
        admin_override: bool = True,
    ) -> PasswordResult:
        """
        Reset password (admin function).
        
        Args:
            joki_id: ID joki
            new_password: Password baru (opsional, akan generate jika None)
            admin_override: Admin override (skip validation)
            
        Returns:
            PasswordResult: Result dengan password baru
        """
        log.info(f"Reset password attempt: joki_id={joki_id}, admin_override={admin_override}")
        
        # ==========================================================
        # 1. VALIDASI JOKI
        # ==========================================================
        try:
            profile = PortalJokiProfileRepository.get(joki_id)
            if not profile:
                log.warning(f"Joki not found: joki_id={joki_id}")
                return PasswordResult.error("Joki tidak ditemukan.")
        except Exception as e:
            log.error(f"Failed to get profile: {e}")
            return PasswordResult.error(f"Gagal mengambil data: {str(e)}")
        
        # ==========================================================
        # 2. GENERATE OR USE PROVIDED PASSWORD
        # ==========================================================
        generated = False
        
        if new_password is None:
            new_password = PortalJokiPasswordService.generate_strong_password()
            generated = True
        
        # Validate password (if not admin override)
        if not admin_override:
            validation = PortalJokiPasswordService.validate_password(new_password)
            if not validation["valid"]:
                return PasswordResult.error(
                    validation["message"],
                    validation["errors"],
                )
        
        # ==========================================================
        # 3. UPDATE PASSWORD
        # ==========================================================
        try:
            new_password_hash = hash_password(new_password)
            success = PortalJokiProfileRepository.update_password(
                joki_id,
                new_password_hash,
            )
            
            if not success:
                log.error(f"Failed to reset password: joki_id={joki_id}")
                return PasswordResult.error("Gagal mereset password.")
            
            log.info(f"Password reset successfully: joki_id={joki_id}, generated={generated}")
            
            return PasswordResult.ok(
                "Password berhasil direset." + (" Password baru: " + new_password if generated else ""),
                {
                    "joki_id": joki_id,
                    "new_password": new_password if generated else None,
                    "generated": generated,
                    "kode": profile.get("kode"),
                    "nama": profile.get("nama"),
                },
            )
            
        except Exception as e:
            log.error(f"Failed to reset password: {e}")
            return PasswordResult.error(f"Gagal mereset password: {str(e)}")

    @staticmethod
    def validate_password(
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
            "letmein", "welcome", "monkey", "dragon", "master",
        }
        
        if password.lower() in common_passwords:
            errors.append("Password terlalu umum/lemah. Gunakan kombinasi yang lebih unik.")
        
        # Check for sequential characters
        if len(password) >= 3:
            for i in range(len(password) - 2):
                if (ord(password[i+1]) == ord(password[i]) + 1 and 
                    ord(password[i+2]) == ord(password[i+1]) + 1):
                    errors.append("Password tidak boleh mengandung urutan karakter (abc, 123, dll).")
                    break
        
        # Check for repeated characters
        if len(password) >= 3:
            for i in range(len(password) - 2):
                if password[i] == password[i+1] == password[i+2]:
                    errors.append("Password tidak boleh mengandung 3 karakter berulang (aaa, 111, dll).")
                    break
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "message": "Password valid." if len(errors) == 0 else " ".join(errors),
            "strength": "weak" if len(errors) > 2 else "medium" if len(errors) > 0 else "strong",
        }

    @staticmethod
    def generate_strong_password(length: int = 10) -> str:
        """
        Generate strong random password.
        
        Args:
            length: Panjang password (default 10)
            
        Returns:
            str: Random password
        """
        # Ensure at least one of each type
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure it meets basic requirements
        if not any(c.isupper() for c in password):
            password = password[:length-1] + secrets.choice(string.ascii_uppercase)
        if not any(c.islower() for c in password):
            password = password[:length-1] + secrets.choice(string.ascii_lowercase)
        if not any(c.isdigit() for c in password):
            password = password[:length-1] + secrets.choice(string.digits)
        
        log.debug(f"Generated strong password: {'*' * length}")
        return password

    @staticmethod
    def has_password(joki_id: int) -> bool:
        """
        Check if joki has password set.
        
        Args:
            joki_id: ID joki
            
        Returns:
            bool: True if has password
        """
        try:
            profile = PortalJokiProfileRepository.get(joki_id)
            return bool(profile and profile.get("password_hash"))
        except Exception as e:
            log.error(f"Failed to check password: {e}")
            return False

    @staticmethod
    def get_password_hash(joki_id: int) -> Optional[str]:
        """
        Get password hash (for admin verification).
        
        Args:
            joki_id: ID joki
            
        Returns:
            str: Password hash or None
        """
        try:
            profile = PortalJokiProfileRepository.get(joki_id)
            return profile.get("password_hash") if profile else None
        except Exception as e:
            log.error(f"Failed to get password hash: {e}")
            return None


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
password_service = PortalJokiPasswordService()