"""
Portal Joki - Profile Repository

Repository untuk mengelola data profile joki.
"""

from typing import Optional, Dict, Any
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiProfileRepository:
    """
    Repository Profile Portal Joki.
    
    Table: joki
    """

    # ==========================================================
    # GET PROFILE
    # ==========================================================

    @staticmethod
    def get(joki_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan profile joki berdasarkan ID.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Data profile joki atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama,
                    kode,
                    no_hp,
                    keterangan,
                    aktif,
                    harga_per_judul,
                    max_absen,
                    password_hash,
                    last_login,
                    created_at,
                    updated_at
                FROM joki
                WHERE id = %s
                LIMIT 1
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get profile: joki_id={joki_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_kode(kode: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan profile joki berdasarkan kode.
        
        Args:
            kode: Kode joki
            
        Returns:
            dict: Data profile joki atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama,
                    kode,
                    no_hp,
                    keterangan,
                    aktif,
                    harga_per_judul,
                    max_absen,
                    password_hash,
                    last_login,
                    created_at,
                    updated_at
                FROM joki
                WHERE LOWER(kode) = LOWER(%s)
                LIMIT 1
                """,
                (kode,),
            )
            result = cur.fetchone()
            log.debug(f"Get profile by kode: {kode} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_public(joki_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan profile publik joki (tanpa data sensitif).
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Data profile publik atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama,
                    kode,
                    no_hp,
                    keterangan,
                    aktif,
                    harga_per_judul,
                    max_absen,
                    last_login,
                    created_at
                FROM joki
                WHERE id = %s
                LIMIT 1
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get public profile: joki_id={joki_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_settings(joki_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan setting joki (harga, max_absen, dll).
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Setting joki atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama,
                    kode,
                    harga_per_judul,
                    max_absen,
                    aktif
                FROM joki
                WHERE id = %s
                LIMIT 1
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get settings: joki_id={joki_id} -> {'found' if result else 'not found'}")
            return result

    # ==========================================================
    # UPDATE PROFILE
    # ==========================================================

    @staticmethod
    def update(
        joki_id: int,
        nama: str,
        no_hp: Optional[str] = None,
        keterangan: Optional[str] = None,
    ) -> bool:
        """
        Update profile joki.
        
        Args:
            joki_id: ID joki
            nama: Nama joki
            no_hp: Nomor HP (opsional)
            keterangan: Keterangan (opsional)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE joki
                    SET
                        nama = %s,
                        no_hp = %s,
                        keterangan = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (nama, no_hp, keterangan, joki_id),
                )
                affected = cur.rowcount
                log.info(f"Updated profile: joki_id={joki_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update profile for joki_id {joki_id}: {e}")
            return False

    @staticmethod
    def update_full(
        joki_id: int,
        data: Dict[str, Any],
    ) -> bool:
        """
        Update full profile joki.
        
        Args:
            joki_id: ID joki
            data: Data lengkap profile
            
        Returns:
            bool: True jika berhasil
        """
        try:
            allowed_fields = [
                "nama", "no_hp", "keterangan", "aktif",
                "harga_per_judul", "max_absen"
            ]
            updates = []
            params = []
            
            for field in allowed_fields:
                if field in data:
                    updates.append(f"{field} = %s")
                    params.append(data[field])
            
            if not updates:
                log.warning(f"No valid fields to update for joki_id: {joki_id}")
                return False
            
            updates.append("updated_at = NOW()")
            params.append(joki_id)
            
            query = f"UPDATE joki SET {', '.join(updates)} WHERE id = %s"
            
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(query, tuple(params))
                affected = cur.rowcount
                log.info(f"Updated full profile: joki_id={joki_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update full profile for joki_id {joki_id}: {e}")
            return False

    @staticmethod
    def update_nama(joki_id: int, nama: str) -> bool:
        """
        Update nama joki.
        
        Args:
            joki_id: ID joki
            nama: Nama baru
            
        Returns:
            bool: True jika berhasil
        """
        return PortalJokiProfileRepository.update_full(
            joki_id, {"nama": nama}
        )

    @staticmethod
    def update_no_hp(joki_id: int, no_hp: str) -> bool:
        """
        Update nomor HP joki.
        
        Args:
            joki_id: ID joki
            no_hp: Nomor HP baru
            
        Returns:
            bool: True jika berhasil
        """
        return PortalJokiProfileRepository.update_full(
            joki_id, {"no_hp": no_hp}
        )

    @staticmethod
    def update_keterangan(joki_id: int, keterangan: str) -> bool:
        """
        Update keterangan joki.
        
        Args:
            joki_id: ID joki
            keterangan: Keterangan baru
            
        Returns:
            bool: True jika berhasil
        """
        return PortalJokiProfileRepository.update_full(
            joki_id, {"keterangan": keterangan}
        )

    @staticmethod
    def update_harga(joki_id: int, harga_per_judul: float) -> bool:
        """
        Update harga per judul joki.
        
        Args:
            joki_id: ID joki
            harga_per_judul: Harga baru
            
        Returns:
            bool: True jika berhasil
        """
        return PortalJokiProfileRepository.update_full(
            joki_id, {"harga_per_judul": harga_per_judul}
        )

    @staticmethod
    def update_max_absen(joki_id: int, max_absen: int) -> bool:
        """
        Update max absen joki.
        
        Args:
            joki_id: ID joki
            max_absen: Max absen baru
            
        Returns:
            bool: True jika berhasil
        """
        return PortalJokiProfileRepository.update_full(
            joki_id, {"max_absen": max_absen}
        )

    @staticmethod
    def update_status(joki_id: int, aktif: bool) -> bool:
        """
        Update status aktif joki.
        
        Args:
            joki_id: ID joki
            aktif: Status aktif (True/False)
            
        Returns:
            bool: True jika berhasil
        """
        return PortalJokiProfileRepository.update_full(
            joki_id, {"aktif": aktif}
        )

    # ==========================================================
    # PASSWORD
    # ==========================================================

    @staticmethod
    def update_password(joki_id: int, password_hash: str) -> bool:
        """
        Update password joki.
        
        Args:
            joki_id: ID joki
            password_hash: Hash password baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE joki
                    SET
                        password_hash = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (password_hash, joki_id),
                )
                affected = cur.rowcount
                log.info(f"Updated password: joki_id={joki_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update password for joki_id {joki_id}: {e}")
            return False

    @staticmethod
    def get_password_hash(joki_id: int) -> Optional[str]:
        """
        Mendapatkan password hash joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            str: Password hash atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT password_hash
                FROM joki
                WHERE id = %s
                LIMIT 1
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            return result["password_hash"] if result else None

    # ==========================================================
    # LAST LOGIN
    # ==========================================================

    @staticmethod
    def update_last_login(joki_id: int) -> bool:
        """
        Update waktu login terakhir.
        
        Args:
            joki_id: ID joki
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE joki
                    SET
                        last_login = NOW()
                    WHERE id = %s
                    """,
                    (joki_id,),
                )
                affected = cur.rowcount
                log.debug(f"Updated last login: joki_id={joki_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update last login for joki_id {joki_id}: {e}")
            return False

    @staticmethod
    def get_last_login(joki_id: int) -> Optional[datetime]:
        """
        Mendapatkan waktu login terakhir.
        
        Args:
            joki_id: ID joki
            
        Returns:
            datetime: Waktu login terakhir atau None
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT last_login
                FROM joki
                WHERE id = %s
                LIMIT 1
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            return result["last_login"] if result else None

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists(joki_id: int) -> bool:
        """
        Cek apakah joki ada.
        
        Args:
            joki_id: ID joki
            
        Returns:
            bool: True jika ada
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM joki
                WHERE id = %s
                """,
                (joki_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists: joki_id={joki_id} -> {result}")
            return result

    @staticmethod
    def exists_kode(kode: str) -> bool:
        """
        Cek apakah kode joki sudah digunakan.
        
        Args:
            kode: Kode joki
            
        Returns:
            bool: True jika kode sudah digunakan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM joki
                WHERE LOWER(kode) = LOWER(%s)
                """,
                (kode,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists kode: {kode} -> {result}")
            return result

    @staticmethod
    def exists_nama(nama: str) -> bool:
        """
        Cek apakah nama joki sudah digunakan.
        
        Args:
            nama: Nama joki
            
        Returns:
            bool: True jika nama sudah digunakan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM joki
                WHERE LOWER(nama) = LOWER(%s)
                """,
                (nama,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists nama: {nama} -> {result}")
            return result

    @staticmethod
    def is_active(joki_id: int) -> bool:
        """
        Cek apakah joki aktif.
        
        Args:
            joki_id: ID joki
            
        Returns:
            bool: True jika aktif
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT aktif
                FROM joki
                WHERE id = %s
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            is_active = bool(result and result["aktif"])
            log.debug(f"Check is active: joki_id={joki_id} -> {is_active}")
            return is_active

    # ==========================================================
    # STATISTICS
    # ==========================================================

    @staticmethod
    def get_stats(joki_id: int) -> Dict[str, Any]:
        """
        Mendapatkan statistik profile joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Statistik profile
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_penugasan,
                    COUNT(*) FILTER (WHERE status = 3) AS total_selesai,
                    COUNT(*) FILTER (WHERE status = 0) AS total_pending,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan
                WHERE joki_id = %s
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get stats: joki_id={joki_id}")
            return result or {}

    @staticmethod
    def get_monthly_stats(joki_id: int, bulan: int, tahun: int) -> Dict[str, Any]:
        """
        Mendapatkan statistik bulanan joki.
        
        Args:
            joki_id: ID joki
            bulan: Bulan (1-12)
            tahun: Tahun (YYYY)
            
        Returns:
            dict: Statistik bulanan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_penugasan,
                    COUNT(*) FILTER (WHERE status = 3) AS total_selesai,
                    COUNT(*) FILTER (WHERE status = 0) AS total_pending,
                    COALESCE(SUM(target_judul), 0) AS total_target,
                    ROUND(
                        (COUNT(*) FILTER (WHERE status = 3))::numeric
                        / NULLIF(COUNT(*), 0)
                        * 100,
                        2
                    ) AS completion_rate
                FROM portal_joki_penugasan
                WHERE
                    joki_id = %s
                    AND EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                """,
                (joki_id, tahun, bulan),
            )
            result = cur.fetchone()
            log.debug(f"Get monthly stats: joki_id={joki_id}, bulan={bulan}, tahun={tahun}")
            return result or {}


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
profile_repo = PortalJokiProfileRepository()