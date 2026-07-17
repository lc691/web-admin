"""
Portal Joki - Kloter Repository

Repository untuk mengelola data kloter.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiKloterRepository:
    """
    Repository Kloter Portal Joki.
    
    Table: kloter
    """

    # ==========================================================
    # LIST / SELECT
    # ==========================================================

    @staticmethod
    def get_all(
        aktif_only: bool = False,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua data kloter.
        
        Args:
            aktif_only: Hanya kloter aktif
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            List[dict]: List kloter
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    id,
                    nama,
                    aktif,
                    created_at,
                    updated_at
                FROM kloter
                WHERE 1=1
            """
            params = []
            
            if aktif_only:
                query += " AND aktif = TRUE"
            
            query += " ORDER BY nama"
            
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get all kloter: rows={len(result)}")
            return result

    @staticmethod
    def get_active() -> List[Dict[str, Any]]:
        """
        Mendapatkan semua kloter aktif.
        
        Returns:
            List[dict]: List kloter aktif
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama
                FROM kloter
                WHERE aktif = TRUE
                ORDER BY nama
                """
            )
            result = cur.fetchall()
            log.debug(f"Get active kloter: rows={len(result)}")
            return result

    @staticmethod
    def get_simple_list() -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar kloter (id, nama) untuk dropdown/select.
        
        Returns:
            List[dict]: List kloter (id, nama)
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama
                FROM kloter
                WHERE aktif = TRUE
                ORDER BY nama
                """
            )
            result = cur.fetchall()
            log.debug(f"Get simple list: rows={len(result)}")
            return result

    # ==========================================================
    # DETAIL
    # ==========================================================

    @staticmethod
    def get_by_id(kloter_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan detail kloter berdasarkan ID.
        
        Args:
            kloter_id: ID kloter
            
        Returns:
            dict: Detail kloter atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama,
                    aktif,
                    created_at,
                    updated_at
                FROM kloter
                WHERE id = %s
                LIMIT 1
                """,
                (kloter_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get by ID: kloter_id={kloter_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_nama(nama: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan kloter berdasarkan nama.
        
        Args:
            nama: Nama kloter
            
        Returns:
            dict: Detail kloter atau None
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nama,
                    aktif,
                    created_at,
                    updated_at
                FROM kloter
                WHERE LOWER(nama) = LOWER(%s)
                LIMIT 1
                """,
                (nama,),
            )
            result = cur.fetchone()
            log.debug(f"Get by nama: {nama} -> {'found' if result else 'not found'}")
            return result

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        nama: str,
        aktif: bool = True,
    ) -> Optional[int]:
        """
        Membuat kloter baru.
        
        Args:
            nama: Nama kloter
            aktif: Status aktif (default True)
            
        Returns:
            int: ID kloter baru atau None jika gagal
        """
        # Cek duplikat nama
        if PortalJokiKloterRepository.exists_nama(nama):
            log.warning(f"Kloter already exists with nama: {nama}")
            return None
        
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    INSERT INTO kloter (
                        nama,
                        aktif,
                        created_at,
                        updated_at
                    ) VALUES (
                        %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                    """,
                    (nama, aktif),
                )
                result = cur.fetchone()
                kloter_id = result["id"] if result else None
                log.info(f"Created kloter: ID={kloter_id}, nama={nama}")
                return kloter_id
        except Exception as e:
            log.error(f"Failed to create kloter: {e}")
            return None

    @staticmethod
    def create_bulk(nama_list: List[str]) -> int:
        """
        Bulk create multiple kloter.
        
        Args:
            nama_list: List nama kloter
            
        Returns:
            int: Jumlah kloter yang berhasil dibuat
        """
        success_count = 0
        
        for nama in nama_list:
            if PortalJokiKloterRepository.create(nama):
                success_count += 1
        
        log.info(f"Bulk create kloter: {success_count}/{len(nama_list)} created")
        return success_count

    # ==========================================================
    # UPDATE
    # ==========================================================

    @staticmethod
    def update(
        kloter_id: int,
        nama: str,
        aktif: Optional[bool] = None,
    ) -> bool:
        """
        Update kloter.
        
        Args:
            kloter_id: ID kloter
            nama: Nama baru
            aktif: Status aktif (opsional)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                if aktif is not None:
                    cur.execute(
                        """
                        UPDATE kloter
                        SET
                            nama = %s,
                            aktif = %s,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (nama, aktif, kloter_id),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE kloter
                        SET
                            nama = %s,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (nama, kloter_id),
                    )
                affected = cur.rowcount
                log.info(f"Updated kloter: ID={kloter_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update kloter ID {kloter_id}: {e}")
            return False

    @staticmethod
    def update_status(kloter_id: int, aktif: bool) -> bool:
        """
        Update status aktif kloter.
        
        Args:
            kloter_id: ID kloter
            aktif: Status aktif (True/False)
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE kloter
                    SET
                        aktif = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (aktif, kloter_id),
                )
                affected = cur.rowcount
                log.info(f"Updated status kloter: ID={kloter_id}, aktif={aktif}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update status kloter ID {kloter_id}: {e}")
            return False

    @staticmethod
    def update_nama(kloter_id: int, nama: str) -> bool:
        """
        Update nama kloter.
        
        Args:
            kloter_id: ID kloter
            nama: Nama baru
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE kloter
                    SET
                        nama = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (nama, kloter_id),
                )
                affected = cur.rowcount
                log.info(f"Updated nama kloter: ID={kloter_id}, nama={nama}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update nama kloter ID {kloter_id}: {e}")
            return False

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(kloter_id: int) -> bool:
        """
        Menghapus kloter.
        
        Args:
            kloter_id: ID kloter
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM kloter
                    WHERE id = %s
                    """,
                    (kloter_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted kloter: ID={kloter_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to delete kloter ID {kloter_id}: {e}")
            return False

    @staticmethod
    def delete_inactive() -> int:
        """
        Menghapus semua kloter non-aktif.
        
        Returns:
            int: Jumlah kloter yang dihapus
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM kloter
                    WHERE aktif = FALSE
                    """
                )
                affected = cur.rowcount
                log.info(f"Deleted inactive kloter: {affected} rows")
                return affected
        except Exception as e:
            log.error(f"Failed to delete inactive kloter: {e}")
            return 0

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists(kloter_id: int) -> bool:
        """
        Cek apakah kloter ada.
        
        Args:
            kloter_id: ID kloter
            
        Returns:
            bool: True jika ada
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM kloter
                WHERE id = %s
                LIMIT 1
                """,
                (kloter_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists: kloter_id={kloter_id} -> {result}")
            return result

    @staticmethod
    def exists_nama(nama: str) -> bool:
        """
        Cek apakah nama kloter sudah digunakan.
        
        Args:
            nama: Nama kloter
            
        Returns:
            bool: True jika nama sudah digunakan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM kloter
                WHERE LOWER(nama) = LOWER(%s)
                LIMIT 1
                """,
                (nama,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists nama: {nama} -> {result}")
            return result

    @staticmethod
    def exists_active(kloter_id: int) -> bool:
        """
        Cek apakah kloter aktif.
        
        Args:
            kloter_id: ID kloter
            
        Returns:
            bool: True jika aktif
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM kloter
                WHERE id = %s AND aktif = TRUE
                LIMIT 1
                """,
                (kloter_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists active: kloter_id={kloter_id} -> {result}")
            return result

    @staticmethod
    def is_active(kloter_id: int) -> bool:
        """
        Cek apakah kloter aktif (alias untuk exists_active).
        
        Args:
            kloter_id: ID kloter
            
        Returns:
            bool: True jika aktif
        """
        return PortalJokiKloterRepository.exists_active(kloter_id)

    # ==========================================================
    # COUNT / STATISTICS
    # ==========================================================

    @staticmethod
    def count(aktif_only: bool = False) -> int:
        """
        Menghitung total kloter.
        
        Args:
            aktif_only: Hanya kloter aktif
            
        Returns:
            int: Total count
        """
        with get_clean_dict_cursor() as cur:
            query = "SELECT COUNT(*) AS total FROM kloter"
            if aktif_only:
                query += " WHERE aktif = TRUE"
            
            cur.execute(query)
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count kloter: {total}" + (f" (aktif_only)" if aktif_only else ""))
            return total

    @staticmethod
    def count_penugasan(kloter_id: int) -> int:
        """
        Menghitung total penugasan untuk kloter.
        
        Args:
            kloter_id: ID kloter
            
        Returns:
            int: Total penugasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM portal_joki_penugasan
                WHERE kloter_id = %s
                """,
                (kloter_id,),
            )
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count penugasan: kloter_id={kloter_id}, total={total}")
            return total

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Mendapatkan statistik kloter.
        
        Returns:
            dict: Statistik kloter
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_kloter,
                    COUNT(*) FILTER (WHERE aktif = TRUE) AS aktif_kloter,
                    COUNT(*) FILTER (WHERE aktif = FALSE) AS nonaktif_kloter,
                    (
                        SELECT COUNT(DISTINCT kloter_id)
                        FROM portal_joki_penugasan
                    ) AS kloter_with_penugasan
                FROM kloter
                """
            )
            result = cur.fetchone()
            log.debug("Get stats kloter")
            return result or {}

    # ==========================================================
    # TODAY / DAILY
    # ==========================================================

    @staticmethod
    def get_today(tanggal: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Mendapatkan kloter dengan jumlah penugasan hari ini.
        
        Args:
            tanggal: Tanggal yang dicek (default: hari ini)
            
        Returns:
            List[dict]: List kloter dengan count penugasan
        """
        if tanggal is None:
            tanggal = date.today()
        
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    k.id,
                    k.nama,
                    COUNT(p.id) AS total_penugasan,
                    COUNT(p.id) FILTER (WHERE p.status = 0) AS pending,
                    COUNT(p.id) FILTER (WHERE p.status = 3) AS selesai
                FROM kloter k
                LEFT JOIN portal_joki_penugasan p
                    ON p.kloter_id = k.id
                    AND p.tanggal = %s
                GROUP BY
                    k.id,
                    k.nama
                ORDER BY
                    k.nama
                """,
                (tanggal,),
            )
            result = cur.fetchall()
            log.debug(f"Get today: tanggal={tanggal}, rows={len(result)}")
            return result

    @staticmethod
    def get_with_penugasan_count() -> List[Dict[str, Any]]:
        """
        Mendapatkan kloter dengan jumlah total penugasan.
        
        Returns:
            List[dict]: List kloter dengan count penugasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    k.id,
                    k.nama,
                    k.aktif,
                    COUNT(p.id) AS total_penugasan,
                    COUNT(p.id) FILTER (WHERE p.status = 0) AS pending,
                    COUNT(p.id) FILTER (WHERE p.status = 3) AS selesai
                FROM kloter k
                LEFT JOIN portal_joki_penugasan p
                    ON p.kloter_id = k.id
                GROUP BY
                    k.id,
                    k.nama,
                    k.aktif
                ORDER BY
                    k.nama
                """
            )
            result = cur.fetchall()
            log.debug(f"Get with penugasan count: rows={len(result)}")
            return result

    @staticmethod
    def get_monthly_stats(
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan statistik bulanan per kloter.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: Statistik per kloter
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    k.id,
                    k.nama,
                    COUNT(p.id) AS total_penugasan,
                    COUNT(p.id) FILTER (WHERE p.status = 3) AS selesai,
                    COALESCE(SUM(p.target_judul), 0) AS total_target
                FROM kloter k
                LEFT JOIN portal_joki_penugasan p
                    ON p.kloter_id = k.id
                    AND EXTRACT(YEAR FROM p.tanggal) = %s
                    AND EXTRACT(MONTH FROM p.tanggal) = %s
                GROUP BY
                    k.id,
                    k.nama
                ORDER BY
                    k.nama
                """,
                (tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Get monthly stats: tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
kloter_repo = PortalJokiKloterRepository()