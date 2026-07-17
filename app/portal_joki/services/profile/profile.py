"""
Portal Joki - Profile Service

Service untuk manajemen profile joki.
"""

from typing import Optional, Dict, Any
from datetime import date, datetime
import re

from app.portal_joki.repositories.profile.profile_repo import (
    PortalJokiProfileRepository,
)
from app.portal_joki.repositories.auth.auth_repo import (
    PortalJokiAuthRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class ProfileResult:
    """
    Result object untuk operasi profile.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[list] = None,
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
    ) -> "ProfileResult":
        """Create success result."""
        return cls(True, message, data or {})
    
    @classmethod
    def error(
        cls,
        message: str,
        errors: Optional[list] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ProfileResult":
        """Create error result."""
        return cls(False, message, data or {}, errors or [])


# ==========================================================
# PROFILE SERVICE
# ==========================================================
class PortalJokiProfileService:
    """
    Service Profile Portal Joki.
    
    Menyediakan fungsi untuk:
    - Get profile (dengan atau tanpa password)
    - Update profile
    - Update nama
    - Update no HP
    - Update keterangan
    - Update settings (harga, max_absen)
    - Validasi profile data
    """

    @staticmethod
    def get(
        joki_id: int,
        include_sensitive: bool = False,
    ) -> ProfileResult:
        """
        Get profile joki.
        
        Args:
            joki_id: ID joki
            include_sensitive: Include password_hash (default False)
            
        Returns:
            ProfileResult: Profile data
        """
        log.info(f"Get profile: joki_id={joki_id}, include_sensitive={include_sensitive}")
        
        try:
            profile = PortalJokiProfileRepository.get(joki_id)
            
            if not profile:
                log.warning(f"Joki not found: joki_id={joki_id}")
                return ProfileResult.error("Joki tidak ditemukan.")
            
            # Remove sensitive data if not requested
            if not include_sensitive and "password_hash" in profile:
                profile.pop("password_hash")
            
            log.debug(f"Profile found: {profile.get('kode')}")
            
            return ProfileResult.ok("OK", profile)
            
        except Exception as e:
            log.error(f"Failed to get profile: {e}")
            return ProfileResult.error(f"Gagal mengambil profile: {str(e)}")

    @staticmethod
    def get_public(joki_id: int) -> ProfileResult:
        """
        Get public profile (without sensitive data).
        
        Args:
            joki_id: ID joki
            
        Returns:
            ProfileResult: Public profile data
        """
        log.info(f"Get public profile: joki_id={joki_id}")
        
        try:
            profile = PortalJokiProfileRepository.get_public(joki_id)
            
            if not profile:
                log.warning(f"Joki not found: joki_id={joki_id}")
                return ProfileResult.error("Joki tidak ditemukan.")
            
            log.debug(f"Public profile found: {profile.get('kode')}")
            
            return ProfileResult.ok("OK", profile)
            
        except Exception as e:
            log.error(f"Failed to get public profile: {e}")
            return ProfileResult.error(f"Gagal mengambil profile: {str(e)}")

    @staticmethod
    def get_settings(joki_id: int) -> ProfileResult:
        """
        Get joki settings (harga, max_absen, dll).
        
        Args:
            joki_id: ID joki
            
        Returns:
            ProfileResult: Settings data
        """
        log.info(f"Get settings: joki_id={joki_id}")
        
        try:
            settings = PortalJokiProfileRepository.get_settings(joki_id)
            
            if not settings:
                log.warning(f"Joki not found: joki_id={joki_id}")
                return ProfileResult.error("Joki tidak ditemukan.")
            
            log.debug(f"Settings found: {settings.get('kode')}")
            
            return ProfileResult.ok("OK", settings)
            
        except Exception as e:
            log.error(f"Failed to get settings: {e}")
            return ProfileResult.error(f"Gagal mengambil settings: {str(e)}")

    @staticmethod
    def update(
        *,
        joki_id: int,
        nama: Optional[str] = None,
        no_hp: Optional[str] = None,
        keterangan: Optional[str] = None,
    ) -> ProfileResult:
        """
        Update profile joki.
        
        Args:
            joki_id: ID joki
            nama: Nama baru (opsional)
            no_hp: Nomor HP baru (opsional)
            keterangan: Keterangan baru (opsional)
            
        Returns:
            ProfileResult: Result status
        """
        log.info(f"Update profile: joki_id={joki_id}")
        
        # ==========================================================
        # 1. VALIDASI JOKI
        # ==========================================================
        try:
            if not PortalJokiProfileRepository.exists(joki_id):
                log.warning(f"Joki not found: joki_id={joki_id}")
                return ProfileResult.error("Joki tidak ditemukan.")
        except Exception as e:
            log.error(f"Failed to check joki exists: {e}")
            return ProfileResult.error(f"Gagal mengecek joki: {str(e)}")
        
        # ==========================================================
        # 2. VALIDASI NAMA
        # ==========================================================
        errors = []
        
        if nama is not None:
            nama = nama.strip()
            if not nama:
                errors.append("Nama tidak boleh kosong.")
            elif len(nama) < 3:
                errors.append("Nama minimal 3 karakter.")
            elif len(nama) > 100:
                errors.append("Nama maksimal 100 karakter.")
            else:
                # Cek duplikat nama (jika berubah)
                try:
                    current = PortalJokiProfileRepository.get(joki_id)
                    if current and current.get("nama") != nama:
                        if PortalJokiAuthRepository.exists_nama(nama):
                            errors.append(f"Nama '{nama}' sudah digunakan oleh joki lain.")
                except Exception as e:
                    log.warning(f"Failed to check nama duplicate: {e}")
        
        # ==========================================================
        # 3. VALIDASI NO HP
        # ==========================================================
        if no_hp is not None:
            no_hp = no_hp.strip()
            if no_hp:
                # Validate phone number format
                # Indonesian phone number format
                phone_pattern = r'^(\+62|62|0)8[1-9][0-9]{6,10}$'
                if not re.match(phone_pattern, no_hp):
                    errors.append("Format nomor HP tidak valid. Contoh: 08123456789")
        
        if errors:
            return ProfileResult.error("Validasi gagal.", errors)
        
        # ==========================================================
        # 4. UPDATE
        # ==========================================================
        try:
            success = PortalJokiProfileRepository.update(
                joki_id=joki_id,
                nama=nama if nama is not None else "",
                no_hp=no_hp if no_hp is not None else "",
                keterangan=keterangan if keterangan is not None else "",
            )
            
            if not success:
                log.error(f"Failed to update profile: joki_id={joki_id}")
                return ProfileResult.error("Gagal memperbarui profile.")
            
            log.info(f"Profile updated: joki_id={joki_id}")
            
            # Get updated profile
            updated = PortalJokiProfileRepository.get(joki_id)
            if updated and "password_hash" in updated:
                updated.pop("password_hash")
            
            return ProfileResult.ok(
                "Profil berhasil diperbarui.",
                updated,
            )
            
        except Exception as e:
            log.error(f"Failed to update profile: {e}")
            return ProfileResult.error(f"Gagal memperbarui profile: {str(e)}")

    @staticmethod
    def update_nama(
        joki_id: int,
        nama: str,
    ) -> ProfileResult:
        """
        Update nama joki.
        
        Args:
            joki_id: ID joki
            nama: Nama baru
            
        Returns:
            ProfileResult: Result status
        """
        log.info(f"Update nama: joki_id={joki_id}, nama={nama}")
        return PortalJokiProfileService.update(
            joki_id=joki_id,
            nama=nama,
        )

    @staticmethod
    def update_no_hp(
        joki_id: int,
        no_hp: str,
    ) -> ProfileResult:
        """
        Update nomor HP joki.
        
        Args:
            joki_id: ID joki
            no_hp: Nomor HP baru
            
        Returns:
            ProfileResult: Result status
        """
        log.info(f"Update no_hp: joki_id={joki_id}")
        return PortalJokiProfileService.update(
            joki_id=joki_id,
            no_hp=no_hp,
        )

    @staticmethod
    def update_keterangan(
        joki_id: int,
        keterangan: str,
    ) -> ProfileResult:
        """
        Update keterangan joki.
        
        Args:
            joki_id: ID joki
            keterangan: Keterangan baru
            
        Returns:
            ProfileResult: Result status
        """
        log.info(f"Update keterangan: joki_id={joki_id}")
        return PortalJokiProfileService.update(
            joki_id=joki_id,
            keterangan=keterangan,
        )

    @staticmethod
    def update_harga(
        joki_id: int,
        harga_per_judul: float,
    ) -> ProfileResult:
        """
        Update harga per judul joki.
        
        Args:
            joki_id: ID joki
            harga_per_judul: Harga baru
            
        Returns:
            ProfileResult: Result status
        """
        log.info(f"Update harga: joki_id={joki_id}, harga={harga_per_judul}")
        
        try:
            if not PortalJokiProfileRepository.exists(joki_id):
                return ProfileResult.error("Joki tidak ditemukan.")
            
            if harga_per_judul < 0:
                return ProfileResult.error("Harga tidak boleh negatif.")
            
            if harga_per_judul > 1000000:
                return ProfileResult.error("Harga maksimal 1.000.000.")
            
            success = PortalJokiProfileRepository.update_harga(
                joki_id, harga_per_judul
            )
            
            if not success:
                return ProfileResult.error("Gagal memperbarui harga.")
            
            log.info(f"Harga updated: joki_id={joki_id}")
            
            return ProfileResult.ok(
                "Harga per judul berhasil diperbarui.",
                {"harga_per_judul": harga_per_judul},
            )
            
        except Exception as e:
            log.error(f"Failed to update harga: {e}")
            return ProfileResult.error(f"Gagal memperbarui harga: {str(e)}")

    @staticmethod
    def update_max_absen(
        joki_id: int,
        max_absen: int,
    ) -> ProfileResult:
        """
        Update max absen joki.
        
        Args:
            joki_id: ID joki
            max_absen: Max absen baru
            
        Returns:
            ProfileResult: Result status
        """
        log.info(f"Update max_absen: joki_id={joki_id}, max_absen={max_absen}")
        
        try:
            if not PortalJokiProfileRepository.exists(joki_id):
                return ProfileResult.error("Joki tidak ditemukan.")
            
            if max_absen < 1:
                return ProfileResult.error("Max absen minimal 1.")
            
            if max_absen > 20:
                return ProfileResult.error("Max absen maksimal 20.")
            
            success = PortalJokiProfileRepository.update_max_absen(
                joki_id, max_absen
            )
            
            if not success:
                return ProfileResult.error("Gagal memperbarui max absen.")
            
            log.info(f"Max absen updated: joki_id={joki_id}")
            
            return ProfileResult.ok(
                "Max absen berhasil diperbarui.",
                {"max_absen": max_absen},
            )
            
        except Exception as e:
            log.error(f"Failed to update max_absen: {e}")
            return ProfileResult.error(f"Gagal memperbarui max absen: {str(e)}")

    @staticmethod
    def update_status(
        joki_id: int,
        aktif: bool,
    ) -> ProfileResult:
        """
        Update status aktif joki.
        
        Args:
            joki_id: ID joki
            aktif: Status aktif
            
        Returns:
            ProfileResult: Result status
        """
        log.info(f"Update status: joki_id={joki_id}, aktif={aktif}")
        
        try:
            if not PortalJokiProfileRepository.exists(joki_id):
                return ProfileResult.error("Joki tidak ditemukan.")
            
            success = PortalJokiProfileRepository.update_status(
                joki_id, aktif
            )
            
            if not success:
                return ProfileResult.error("Gagal memperbarui status.")
            
            status_text = "diaktifkan" if aktif else "dinonaktifkan"
            log.info(f"Status updated: joki_id={joki_id}, {status_text}")
            
            return ProfileResult.ok(
                f"Joki berhasil {status_text}.",
                {"aktif": aktif},
            )
            
        except Exception as e:
            log.error(f"Failed to update status: {e}")
            return ProfileResult.error(f"Gagal memperbarui status: {str(e)}")

    @staticmethod
    def get_stats(joki_id: int) -> ProfileResult:
        """
        Get profile statistics.
        
        Args:
            joki_id: ID joki
            
        Returns:
            ProfileResult: Statistics data
        """
        log.info(f"Get profile stats: joki_id={joki_id}")
        
        try:
            if not PortalJokiProfileRepository.exists(joki_id):
                return ProfileResult.error("Joki tidak ditemukan.")
            
            stats = PortalJokiProfileRepository.get_stats(joki_id)
            monthly_stats = PortalJokiProfileRepository.get_monthly_stats(
                joki_id,
                datetime.now().month,
                datetime.now().year,
            )
            
            return ProfileResult.ok(
                "OK",
                {
                    "overall": stats,
                    "monthly": monthly_stats,
                    "joki_id": joki_id,
                },
            )
            
        except Exception as e:
            log.error(f"Failed to get stats: {e}")
            return ProfileResult.error(f"Gagal mengambil statistik: {str(e)}")


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
profile_service = PortalJokiProfileService()