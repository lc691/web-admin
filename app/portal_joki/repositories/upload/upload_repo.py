"""
Portal Joki - Upload Repository

Repository untuk mengelola data upload penugasan joki.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiUploadRepository:
    """
    Repository Upload Portal Joki.
    
    Table: portal_joki_upload
    """

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        *,
        penugasan_id: int,
        file_path: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
        nomor: int,
        catatan: Optional[str] = None,
    ) -> Optional[int]:
        """
        Membuat upload baru.
        
        Args:
            penugasan_id: ID penugasan
            file_path: Path file yang diupload
            original_filename: Nama file asli
            mime_type: Tipe MIME file
            file_size: Ukuran file dalam bytes
            nomor: Nomor urut upload
            catatan: Catatan tambahan (opsional)
            
        Returns:
            int: ID upload baru atau None jika gagal
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    INSERT INTO portal_joki_upload (
                        penugasan_id,
                        file_path,
                        catatan,
                        original_filename,
                        mime_type,
                        file_size,
                        nomor,
                        uploaded_at,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                    """,
                    (
                        penugasan_id,
                        file_path,
                        catatan,
                        original_filename,
                        mime_type,
                        file_size,
                        nomor,
                    ),
                )
                result = cur.fetchone()
                upload_id = result["id"] if result else None
                log.info(f"Created upload: ID={upload_id}, penugasan_id={penugasan_id}, file={original_filename}")
                return upload_id
        except Exception as e:
            log.error(f"Failed to create upload: {e}")
            return None

    @staticmethod
    def create_bulk(uploads: List[Dict[str, Any]]) -> int:
        """
        Bulk create multiple uploads.
        
        Args:
            uploads: List data upload
            
        Returns:
            int: Jumlah upload yang berhasil dibuat
        """
        success_count = 0
        
        for data in uploads:
            if PortalJokiUploadRepository.create(**data):
                success_count += 1
        
        log.info(f"Bulk create uploads: {success_count}/{len(uploads)} created")
        return success_count

    # ==========================================================
    # GET / SELECT
    # ==========================================================

    @staticmethod
    def get(upload_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan detail upload berdasarkan ID.
        
        Args:
            upload_id: ID upload
            
        Returns:
            dict: Detail upload atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM portal_joki_upload
                WHERE id = %s
                LIMIT 1
                """,
                (upload_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get upload: upload_id={upload_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_penugasan(
        penugasan_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua upload untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            List[dict]: List upload
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT *
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                ORDER BY nomor, uploaded_at DESC
            """
            params = [penugasan_id]
            
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get by penugasan: penugasan_id={penugasan_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_latest_by_penugasan(
        penugasan_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan upload terbaru untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Upload terbaru atau None
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                ORDER BY uploaded_at DESC, id DESC
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get latest by penugasan: penugasan_id={penugasan_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_joki(
        joki_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua upload untuk joki.
        
        Args:
            joki_id: ID joki
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            List[dict]: List upload dengan detail penugasan
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    u.*,
                    p.tanggal,
                    p.kloter_id,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                WHERE p.joki_id = %s
                ORDER BY
                    p.tanggal DESC,
                    u.nomor,
                    u.uploaded_at DESC
            """
            params = [joki_id]
            
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get by joki: joki_id={joki_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_by_kloter(
        kloter_id: int,
        tanggal: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan upload berdasarkan kloter.
        
        Args:
            kloter_id: ID kloter
            tanggal: Filter tanggal (opsional)
            
        Returns:
            List[dict]: List upload
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    u.*,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                WHERE p.kloter_id = %s
            """
            params = [kloter_id]
            
            if tanggal is not None:
                query += " AND p.tanggal = %s"
                params.append(tanggal)
            
            query += """
                ORDER BY
                    p.tanggal DESC,
                    j.nama,
                    u.nomor,
                    u.uploaded_at DESC
            """
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get by kloter: kloter_id={kloter_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_by_date(
        tanggal: date,
        joki_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan upload berdasarkan tanggal.
        
        Args:
            tanggal: Tanggal upload
            joki_id: Filter by joki (opsional)
            
        Returns:
            List[dict]: List upload
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    u.*,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.tanggal = %s
            """
            params = [tanggal]
            
            if joki_id is not None:
                query += " AND p.joki_id = %s"
                params.append(joki_id)
            
            query += """
                ORDER BY
                    j.nama,
                    u.nomor,
                    u.uploaded_at DESC
            """
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get by date: tanggal={tanggal}, rows={len(result)}")
            return result

    @staticmethod
    def get_all(
        limit: Optional[int] = None,
        offset: int = 0,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        joki_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua upload dengan filter.
        
        Args:
            limit: Jumlah data per page
            offset: Offset untuk pagination
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            joki_id: Filter by joki
            
        Returns:
            List[dict]: List upload dengan detail
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    u.*,
                    p.tanggal,
                    p.kloter_id,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE 1=1
            """
            params = []
            
            if start_date is not None:
                query += " AND p.tanggal >= %s"
                params.append(start_date)
            
            if end_date is not None:
                query += " AND p.tanggal <= %s"
                params.append(end_date)
            
            if joki_id is not None:
                query += " AND p.joki_id = %s"
                params.append(joki_id)
            
            query += """
                ORDER BY
                    p.tanggal DESC,
                    j.nama,
                    u.nomor,
                    u.uploaded_at DESC
            """
            
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get all uploads: rows={len(result)}")
            return result

    @staticmethod
    def get_recent(limit: int = 20) -> List[Dict[str, Any]]:
        """
        Mendapatkan upload terbaru.
        
        Args:
            limit: Jumlah data yang diambil
            
        Returns:
            List[dict]: List upload terbaru
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.*,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                ORDER BY u.uploaded_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            result = cur.fetchall()
            log.debug(f"Get recent uploads: rows={len(result)}")
            return result

    @staticmethod
    def get_by_file_path(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan upload berdasarkan file path.
        
        Args:
            file_path: Path file
            
        Returns:
            dict: Data upload atau None
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM portal_joki_upload
                WHERE file_path = %s
                LIMIT 1
                """,
                (file_path,),
            )
            result = cur.fetchone()
            log.debug(f"Get by file path: {'found' if result else 'not found'}")
            return result

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(upload_id: int) -> bool:
        """
        Menghapus upload.
        
        Args:
            upload_id: ID upload
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_upload
                    WHERE id = %s
                    """,
                    (upload_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted upload: upload_id={upload_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to delete upload_id {upload_id}: {e}")
            return False

    @staticmethod
    def delete_by_penugasan(penugasan_id: int) -> int:
        """
        Menghapus semua upload untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            int: Jumlah upload yang dihapus
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_upload
                    WHERE penugasan_id = %s
                    """,
                    (penugasan_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted uploads by penugasan: penugasan_id={penugasan_id}, affected={affected}")
                return affected
        except Exception as e:
            log.error(f"Failed to delete uploads for penugasan_id {penugasan_id}: {e}")
            return 0

    @staticmethod
    def delete_by_joki(joki_id: int) -> int:
        """
        Menghapus semua upload untuk joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            int: Jumlah upload yang dihapus
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_upload u
                    USING portal_joki_penugasan p
                    WHERE u.penugasan_id = p.id
                      AND p.joki_id = %s
                    """,
                    (joki_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted uploads by joki: joki_id={joki_id}, affected={affected}")
                return affected
        except Exception as e:
            log.error(f"Failed to delete uploads for joki_id {joki_id}: {e}")
            return 0

    # ==========================================================
    # COUNT / STATISTICS
    # ==========================================================

    @staticmethod
    def count_by_penugasan(penugasan_id: int) -> int:
        """
        Menghitung total upload untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            int: Total upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count by penugasan: penugasan_id={penugasan_id}, total={total}")
            return total

    @staticmethod
    def count_by_joki(joki_id: int) -> int:
        """
        Menghitung total upload untuk joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            int: Total upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                WHERE p.joki_id = %s
                """,
                (joki_id,),
            )
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count by joki: joki_id={joki_id}, total={total}")
            return total

    @staticmethod
    def get_stats(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Mendapatkan statistik upload.
        
        Args:
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            
        Returns:
            dict: Statistik upload
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    COUNT(*) AS total_uploads,
                    COUNT(DISTINCT penugasan_id) AS total_penugasan,
                    COUNT(DISTINCT p.joki_id) AS total_joki,
                    SUM(file_size) AS total_size_bytes,
                    AVG(file_size) AS avg_size_bytes,
                    COUNT(*) FILTER (WHERE u.uploaded_at >= NOW() - INTERVAL '24 hours') AS uploads_24h
                FROM portal_joki_upload u
                JOIN portal_joki_penugasan p ON p.id = u.penugasan_id
                WHERE 1=1
            """
            params = []
            
            if start_date is not None:
                query += " AND p.tanggal >= %s"
                params.append(start_date)
            
            if end_date is not None:
                query += " AND p.tanggal <= %s"
                params.append(end_date)
            
            cur.execute(query, tuple(params))
            result = cur.fetchone()
            log.debug("Get upload stats")
            return result or {}

    @staticmethod
    def get_daily_stats(days: int = 7) -> List[Dict[str, Any]]:
        """
        Mendapatkan statistik upload harian.
        
        Args:
            days: Jumlah hari ke belakang
            
        Returns:
            List[dict]: Statistik per hari
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    DATE(u.uploaded_at) AS tanggal,
                    COUNT(*) AS total,
                    COUNT(DISTINCT penugasan_id) AS total_penugasan,
                    SUM(file_size) AS total_size_bytes
                FROM portal_joki_upload u
                WHERE u.uploaded_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(u.uploaded_at)
                ORDER BY tanggal DESC
                """,
                (days,),
            )
            result = cur.fetchall()
            log.debug(f"Get daily stats: days={days}, rows={len(result)}")
            return result

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def exists(upload_id: int) -> bool:
        """
        Cek apakah upload ada.
        
        Args:
            upload_id: ID upload
            
        Returns:
            bool: True jika ada
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_upload
                WHERE id = %s
                """,
                (upload_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists: upload_id={upload_id} -> {result}")
            return result

    @staticmethod
    def has_upload(penugasan_id: int) -> bool:
        """
        Cek apakah penugasan sudah memiliki upload.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            bool: True jika ada upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check has upload: penugasan_id={penugasan_id} -> {result}")
            return result

    @staticmethod
    def has_upload_by_nomor(
        penugasan_id: int,
        nomor: int,
    ) -> bool:
        """
        Cek apakah penugasan sudah memiliki upload dengan nomor tertentu.
        
        Args:
            penugasan_id: ID penugasan
            nomor: Nomor upload
            
        Returns:
            bool: True jika ada upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_upload
                WHERE penugasan_id = %s AND nomor = %s
                LIMIT 1
                """,
                (penugasan_id, nomor),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check has upload by nomor: penugasan_id={penugasan_id}, nomor={nomor} -> {result}")
            return result

    @staticmethod
    def get_next_nomor(penugasan_id: int) -> int:
        """
        Mendapatkan nomor upload berikutnya untuk penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            int: Nomor berikutnya
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(nomor), 0) + 1 AS next_nomor
                FROM portal_joki_upload
                WHERE penugasan_id = %s
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            next_nomor = result["next_nomor"] if result else 1
            log.debug(f"Get next nomor: penugasan_id={penugasan_id}, next_nomor={next_nomor}")
            return next_nomor


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
upload_repo = PortalJokiUploadRepository()