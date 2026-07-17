"""
Portal Joki - Authentication Repository

Repository ini hanya bertugas mengambil / mengubah data.
Tidak ada business logic (password verify, session, dll).
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.database import get_clean_dict_cursor, get_dict_cursor
from app.utils.logger import log


class PortalJokiAuthRepository:
    """
    Repository Authentication Portal Joki.
    
    Table: joki
    Columns:
        - id: integer (PK)
        - kode: varchar(20) (UNIQUE)
        - nama: varchar(100) (UNIQUE)
        - password_hash: text
        - no_hp: varchar(20)
        - keterangan: text
        - aktif: boolean (default true)
        - harga_per_judul: numeric(10,2) (default 180)
        - max_absen: smallint (default 4)
        - last_login: timestamp
        - created_at: timestamp (default now())
        - updated_at: timestamp (default now())
    """

    # ==========================================================
    # SELECT / READ
    # ==========================================================

    @staticmethod
    def get_by_kode(kode: str) -> Optional[Dict[str, Any]]:
        """
        Mengambil data joki berdasarkan kode login (case-insensitive).
        
        Args:
            kode: Kode login joki
            
        Returns:
            dict: Data joki atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    kode,
                    nama,
                    password_hash,
                    no_hp,
                    keterangan,
                    aktif,
                    harga_per_judul,
                    max_absen,
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
            log.debug(f"Get joki by kode: {kode} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_id(joki_id: int) -> Optional[Dict[str, Any]]:
        """
        Mengambil data joki berdasarkan ID.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Data joki atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    kode,
                    nama,
                    no_hp,
                    keterangan,
                    aktif,
                    harga_per_judul,
                    max_absen,
                    last_login,
                    created_at,
                    updated_at
                FROM joki
                WHERE id = %s
                LIMIT 1
                """,
                (joki_id,),
            )
            return cur.fetchone()

    @staticmethod
    def get_by_nama(nama: str) -> Optional[Dict[str, Any]]:
        """
        Mengambil data joki berdasarkan nama.
        
        Args:
            nama: Nama joki
            
        Returns:
            dict: Data joki atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    kode,
                    nama,
                    no_hp,
                    keterangan,
                    aktif,
                    harga_per_judul,
                    max_absen,
                    last_login
                FROM joki
                WHERE LOWER(nama) = LOWER(%s)
                LIMIT 1
                """,
                (nama,),
            )
            return cur.fetchone()

    @staticmethod
    def get_all(
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
        order_by: str = "id",
        order_dir: str = "DESC",
    ) -> List[Dict[str, Any]]:
        """
        Mengambil semua data joki dengan pagination.
        
        Args:
            limit: Jumlah data per page
            offset: Offset untuk pagination
            active_only: Hanya joki aktif
            order_by: Field untuk sorting
            order_dir: ASC atau DESC
            
        Returns:
            List[dict]: List data joki
        """
        # Validasi order_by untuk mencegah SQL injection
        allowed_order = ["id", "kode", "nama", "last_login", "created_at", "harga_per_judul", "max_absen"]
        if order_by not in allowed_order:
            order_by = "id"
        
        if order_dir.upper() not in ["ASC", "DESC"]:
            order_dir = "DESC"
        
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    id,
                    kode,
                    nama,
                    no_hp,
                    keterangan,
                    aktif,
                    harga_per_judul,
                    max_absen,
                    last_login,
                    created_at
                FROM joki
            """
            params = []
            
            if active_only:
                query += " WHERE aktif = TRUE"
            
            query += f" ORDER BY {order_by} {order_dir} LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            return cur.fetchall()

    @staticmethod
    def get_active() -> List[Dict[str, Any]]:
        """
        Mengambil semua joki aktif.
        
        Returns:
            List[dict]: List joki aktif
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    kode,
                    nama,
                    no_hp,
                    harga_per_judul,
                    max_absen
                FROM joki
                WHERE aktif = TRUE
                ORDER BY nama ASC
                """
            )
            return cur.fetchall()

    @staticmethod
    def get_simple_list() -> List[Dict[str, Any]]:
        """
        Mengambil daftar joki (hanya id, kode, nama) untuk dropdown/select.
        
        Returns:
            List[dict]: List joki (id, kode, nama)
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    kode,
                    nama
                FROM joki
                WHERE aktif = TRUE
                ORDER BY nama ASC
                """
            )
            return cur.fetchall()

    @staticmethod
    def search(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Mencari joki berdasarkan keyword.
        
        Args:
            keyword: Keyword untuk search (kode, nama, atau no_hp)
            limit: Batas hasil
            
        Returns:
            List[dict]: List joki yang match
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    kode,
                    nama,
                    no_hp,
                    aktif,
                    harga_per_judul,
                    max_absen
                FROM joki
                WHERE LOWER(kode) LIKE LOWER(%s)
                   OR LOWER(nama) LIKE LOWER(%s)
                   OR no_hp LIKE %s
                ORDER BY nama ASC
                LIMIT %s
                """,
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit),
            )
            return cur.fetchall()

    @staticmethod
    def count(active_only: bool = False) -> int:
        """
        Menghitung total joki.
        
        Args:
            active_only: Hanya joki aktif
            
        Returns:
            int: Total count
        """
        with get_clean_dict_cursor() as cur:
            query = "SELECT COUNT(*) as total FROM joki"
            if active_only:
                query += " WHERE aktif = TRUE"
            
            cur.execute(query)
            result = cur.fetchone()
            return result["total"] if result else 0

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Mendapatkan statistik joki.
        
        Returns:
            dict: Statistik (total, aktif, nonaktif, dll)
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN aktif = TRUE THEN 1 ELSE 0 END) as aktif,
                    SUM(CASE WHEN aktif = FALSE THEN 1 ELSE 0 END) as nonaktif,
                    AVG(harga_per_judul) as avg_harga,
                    MAX(harga_per_judul) as max_harga,
                    MIN(harga_per_judul) as min_harga,
                    AVG(max_absen) as avg_max_absen,
                    MAX(max_absen) as max_max_absen,
                    COUNT(DISTINCT kode) as unique_kode
                FROM joki
                """
            )
            result = cur.fetchone()
            
            # Tambahkan last login stats
            cur.execute(
                """
                SELECT
                    COUNT(*) as logged_in_24h
                FROM joki
                WHERE last_login >= NOW() - INTERVAL '24 hours'
                """
            )
            last_login = cur.fetchone()
            
            result["logged_in_24h"] = last_login["logged_in_24h"] if last_login else 0
            
            return result

    @staticmethod
    def get_by_ids(joki_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Mengambil data joki berdasarkan multiple IDs.
        
        Args:
            joki_ids: List ID joki
            
        Returns:
            List[dict]: List data joki
        """
        if not joki_ids:
            return []
        
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    kode,
                    nama,
                    no_hp,
                    aktif,
                    harga_per_judul,
                    max_absen
                FROM joki
                WHERE id = ANY(%s)
                ORDER BY nama ASC
                """,
                (joki_ids,),
            )
            return cur.fetchall()

    # ==========================================================
    # UPDATE
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
                log.info(f"Password updated for joki_id: {joki_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update password for joki_id {joki_id}: {e}")
            return False

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
                        last_login = NOW(),
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (joki_id,),
                )
                affected = cur.rowcount
                log.debug(f"Last login updated for joki_id: {joki_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update last login for joki_id {joki_id}: {e}")
            return False

    @staticmethod
    def update_profile(joki_id: int, data: Dict[str, Any]) -> bool:
        """
        Update profile joki.
        
        Args:
            joki_id: ID joki
            data: Data yang akan diupdate
            
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
                log.info(f"Profile updated for joki_id: {joki_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update profile for joki_id {joki_id}: {e}")
            return False

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
        return PortalJokiAuthRepository.update_profile(
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
        return PortalJokiAuthRepository.update_profile(
            joki_id, {"max_absen": max_absen}
        )

    # ==========================================================
    # CREATE / INSERT
    # ==========================================================

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[int]:
        """
        Membuat joki baru.
        
        Args:
            data: Data joki (kode, nama, password_hash, no_hp, dll)
            
        Returns:
            int: ID joki baru atau None jika gagal
        """
        required_fields = ["kode", "nama", "password_hash"]
        
        # Validasi required fields
        for field in required_fields:
            if field not in data or not data[field]:
                log.error(f"Missing required field: {field}")
                return None
        
        # Cek duplikat kode
        if PortalJokiAuthRepository.exists(data["kode"]):
            log.error(f"Kode already exists: {data['kode']}")
            return None
        
        # Cek duplikat nama
        if PortalJokiAuthRepository.exists_nama(data["nama"]):
            log.error(f"Nama already exists: {data['nama']}")
            return None
        
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    INSERT INTO joki (
                        kode,
                        nama,
                        password_hash,
                        no_hp,
                        keterangan,
                        aktif,
                        harga_per_judul,
                        max_absen,
                        created_at,
                        updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                    """,
                    (
                        data["kode"],
                        data["nama"],
                        data["password_hash"],
                        data.get("no_hp"),
                        data.get("keterangan"),
                        data.get("aktif", True),
                        data.get("harga_per_judul", 180),
                        data.get("max_absen", 4),
                    ),
                )
                result = cur.fetchone()
                joki_id = result["id"] if result else None
                log.info(f"Created new joki: {data['kode']} (ID: {joki_id})")
                return joki_id
        except Exception as e:
            log.error(f"Failed to create joki: {e}")
            return None

    # ==========================================================
    # DELETE / SOFT DELETE
    # ==========================================================

    @staticmethod
    def delete(joki_id: int, hard_delete: bool = False) -> bool:
        """
        Menghapus joki.
        
        Args:
            joki_id: ID joki
            hard_delete: True untuk hard delete, False untuk soft delete
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                if hard_delete:
                    cur.execute(
                        "DELETE FROM joki WHERE id = %s",
                        (joki_id,),
                    )
                else:
                    # Soft delete - set aktif = FALSE
                    cur.execute(
                        """
                        UPDATE joki
                        SET
                            aktif = FALSE,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (joki_id,),
                    )
                
                affected = cur.rowcount
                log.info(f"Joki deleted (hard={hard_delete}): {joki_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to delete joki_id {joki_id}: {e}")
            return False

    @staticmethod
    def restore(joki_id: int) -> bool:
        """
        Merestore joki yang soft delete.
        
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
                        aktif = TRUE,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (joki_id,),
                )
                affected = cur.rowcount
                log.info(f"Joki restored: {joki_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to restore joki_id {joki_id}: {e}")
            return False

    # ==========================================================
    # BULK OPERATIONS
    # ==========================================================

    @staticmethod
    def bulk_create(data_list: List[Dict[str, Any]]) -> int:
        """
        Bulk create multiple joki.
        
        Args:
            data_list: List data joki
            
        Returns:
            int: Jumlah joki yang berhasil dibuat
        """
        success_count = 0
        
        for data in data_list:
            if PortalJokiAuthRepository.create(data):
                success_count += 1
        
        log.info(f"Bulk create: {success_count}/{len(data_list)} joki created")
        return success_count

    @staticmethod
    def bulk_update_status(joki_ids: List[int], aktif: bool) -> int:
        """
        Bulk update status joki.
        
        Args:
            joki_ids: List ID joki
            aktif: Status aktif (True/False)
            
        Returns:
            int: Jumlah joki yang berhasil diupdate
        """
        if not joki_ids:
            return 0
        
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE joki
                    SET
                        aktif = %s,
                        updated_at = NOW()
                    WHERE id = ANY(%s)
                    """,
                    (aktif, joki_ids),
                )
                affected = cur.rowcount
                log.info(f"Bulk update status: {affected} joki updated to aktif={aktif}")
                return affected
        except Exception as e:
            log.error(f"Failed to bulk update status: {e}")
            return 0

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists(kode: str) -> bool:
        """
        Cek apakah kode joki sudah digunakan.
        
        Args:
            kode: Kode login joki
            
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
            log.debug(f"Check kode exists: {kode} -> {result}")
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
            log.debug(f"Check nama exists: {nama} -> {result}")
            return result

    @staticmethod
    def is_active(joki_id: int) -> bool:
        """
        Cek apakah joki masih aktif.
        
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
            row = cur.fetchone()
            is_active = bool(row and row["aktif"])
            log.debug(f"Check joki active: {joki_id} -> {is_active}")
            return is_active

    @staticmethod
    def get_max_absen(joki_id: int) -> int:
        """
        Mendapatkan max_absen joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            int: Max absen (default 4 jika tidak ditemukan)
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT max_absen
                FROM joki
                WHERE id = %s
                """,
                (joki_id,),
            )
            row = cur.fetchone()
            return row["max_absen"] if row else 4


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
auth_repo = PortalJokiAuthRepository()