"""
Portal Joki - Penugasan Repository

Repository untuk mengelola data penugasan joki.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiPenugasanRepository:
    """
    Repository Penugasan Portal Joki.
    
    Table: portal_joki_penugasan
    """

    # ==========================================================
    # STATUS CONSTANTS
    # ==========================================================
    STATUS_PENDING = 0
    STATUS_UPLOAD = 1
    STATUS_REVISI = 2
    STATUS_SELESAI = 3
    
    STATUS_LABELS = {
        0: "Pending",
        1: "Upload",
        2: "Revisi",
        3: "Selesai",
    }
    
    STATUS_COLORS = {
        0: "warning",
        1: "info",
        2: "danger",
        3: "success",
    }

    # ==========================================================
    # LIST / SELECT
    # ==========================================================

    @staticmethod
    def get_datatable(
        limit: Optional[int] = None,
        offset: int = 0,
        status: Optional[int] = None,
        joki_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan data penugasan untuk datatable dengan filter.
        
        Args:
            limit: Jumlah data per page
            offset: Offset untuk pagination
            status: Filter by status
            joki_id: Filter by joki
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            
        Returns:
            List[dict]: List penugasan
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    p.id,
                    p.tanggal,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    p.absen_awal,
                    p.absen_akhir,
                    p.target_judul,
                    p.status,
                    p.deadline,
                    p.created_at,
                    p.updated_at
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE 1=1
            """
            params = []
            
            if status is not None:
                query += " AND p.status = %s"
                params.append(status)
            
            if joki_id is not None:
                query += " AND p.joki_id = %s"
                params.append(joki_id)
            
            if start_date is not None:
                query += " AND p.tanggal >= %s"
                params.append(start_date)
            
            if end_date is not None:
                query += " AND p.tanggal <= %s"
                params.append(end_date)
            
            query += """
                ORDER BY
                    p.tanggal DESC,
                    j.nama,
                    p.kloter_id
            """
            
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get datatable: rows={len(result)}")
            return result

    @staticmethod
    def get_by_date(
        tanggal: date,
        joki_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan penugasan berdasarkan tanggal.
        
        Args:
            tanggal: Tanggal yang dicari
            joki_id: Filter by joki (opsional)
            
        Returns:
            List[dict]: List penugasan
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_penugasan p
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
                    p.kloter_id,
                    p.absen_awal
            """
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get by date: tanggal={tanggal}, rows={len(result)}")
            return result

    @staticmethod
    def get_by_joki(
        joki_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan penugasan berdasarkan joki.
        
        Args:
            joki_id: ID joki
            limit: Jumlah data per page
            offset: Offset untuk pagination
            
        Returns:
            List[dict]: List penugasan
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.joki_id = %s
                ORDER BY
                    p.tanggal DESC,
                    p.kloter_id,
                    p.absen_awal
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
    def get_by_joki_date(
        joki_id: int,
        tanggal: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan penugasan joki pada tanggal tertentu.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal yang dicari
            
        Returns:
            List[dict]: List penugasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.*,
                    k.nama AS kloter_nama
                FROM portal_joki_penugasan p
                JOIN kloter k ON k.id = p.kloter_id
                WHERE
                    p.joki_id = %s
                    AND p.tanggal = %s
                ORDER BY
                    p.kloter_id,
                    p.absen_awal
                """,
                (joki_id, tanggal),
            )
            result = cur.fetchall()
            log.debug(f"Get by joki date: joki_id={joki_id}, tanggal={tanggal}, rows={len(result)}")
            return result

    @staticmethod
    def get_by_kloter(
        kloter_id: int,
        tanggal: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan penugasan berdasarkan kloter.
        
        Args:
            kloter_id: ID kloter
            tanggal: Filter tanggal (opsional)
            
        Returns:
            List[dict]: List penugasan
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                WHERE p.kloter_id = %s
            """
            params = [kloter_id]
            
            if tanggal is not None:
                query += " AND p.tanggal = %s"
                params.append(tanggal)
            
            query += """
                ORDER BY
                    j.nama,
                    p.absen_awal
            """
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get by kloter: kloter_id={kloter_id}, rows={len(result)}")
            return result

    @staticmethod
    def get_by_status(
        status: int,
        tanggal: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan penugasan berdasarkan status.
        
        Args:
            status: Status penugasan
            tanggal: Filter tanggal (opsional)
            
        Returns:
            List[dict]: List penugasan
        """
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.status = %s
            """
            params = [status]
            
            if tanggal is not None:
                query += " AND p.tanggal = %s"
                params.append(tanggal)
            
            query += """
                ORDER BY
                    p.tanggal DESC,
                    j.nama
            """
            
            cur.execute(query, tuple(params))
            result = cur.fetchall()
            log.debug(f"Get by status: status={status}, rows={len(result)}")
            return result

    # ==========================================================
    # DETAIL
    # ==========================================================

    @staticmethod
    def get(penugasan_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan detail penugasan berdasarkan ID.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Detail penugasan atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    u.id AS upload_id,
                    u.file_path,
                    u.uploaded_at,
                    r.status AS review_status,
                    r.komentar,
                    r.reviewed_at
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                LEFT JOIN LATERAL (
                    SELECT
                        id,
                        file_path,
                        uploaded_at
                    FROM portal_joki_upload
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) u ON TRUE
                LEFT JOIN LATERAL (
                    SELECT
                        status,
                        komentar,
                        reviewed_at
                    FROM portal_joki_review
                    WHERE penugasan_id = p.id
                    ORDER BY id DESC
                    LIMIT 1
                ) r ON TRUE
                WHERE p.id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get detail: penugasan_id={penugasan_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_with_upload_history(penugasan_id: int) -> Dict[str, Any]:
        """
        Mendapatkan detail penugasan dengan history upload.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            dict: Detail penugasan dengan history upload
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.*,
                    j.nama AS joki_nama,
                    j.kode AS joki_kode,
                    k.nama AS kloter_nama,
                    (
                        SELECT json_agg(
                            json_build_object(
                                'id', u.id,
                                'file_path', u.file_path,
                                'uploaded_at', u.uploaded_at
                            ) ORDER BY u.id DESC
                        )
                        FROM portal_joki_upload u
                        WHERE u.penugasan_id = p.id
                    ) AS upload_history,
                    (
                        SELECT json_agg(
                            json_build_object(
                                'id', r.id,
                                'status', r.status,
                                'komentar', r.komentar,
                                'reviewed_at', r.reviewed_at
                            ) ORDER BY r.id DESC
                        )
                        FROM portal_joki_review r
                        WHERE r.penugasan_id = p.id
                    ) AS review_history
                FROM portal_joki_penugasan p
                JOIN joki j ON j.id = p.joki_id
                JOIN kloter k ON k.id = p.kloter_id
                WHERE p.id = %s
                LIMIT 1
                """,
                (penugasan_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get with upload history: penugasan_id={penugasan_id}")
            return result or {}

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        tanggal: date,
        joki_id: int,
        kloter_id: int,
        absen_awal: int,
        absen_akhir: int,
        target_judul: int,
        instruksi: Optional[str] = None,
        deadline: Optional[date] = None,
        created_by: Optional[str] = None,
    ) -> Optional[int]:
        """
        Membuat penugasan baru.
        
        Args:
            tanggal: Tanggal penugasan
            joki_id: ID joki
            kloter_id: ID kloter
            absen_awal: Absen awal
            absen_akhir: Absen akhir
            target_judul: Target judul
            instruksi: Instruksi tambahan
            deadline: Deadline
            created_by: Pembuat
            
        Returns:
            int: ID penugasan baru atau None jika gagal
        """
        # Cek konflik absen
        if PortalJokiPenugasanRepository.exists_absen_conflict(
            tanggal, joki_id, absen_awal, absen_akhir
        ):
            log.warning(f"Absen conflict: tanggal={tanggal}, joki_id={joki_id}")
            return None
        
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    INSERT INTO portal_joki_penugasan (
                        tanggal,
                        joki_id,
                        kloter_id,
                        absen_awal,
                        absen_akhir,
                        target_judul,
                        instruksi,
                        deadline,
                        status,
                        created_by,
                        updated_by,
                        created_at,
                        updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        0, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                    """,
                    (
                        tanggal,
                        joki_id,
                        kloter_id,
                        absen_awal,
                        absen_akhir,
                        target_judul,
                        instruksi,
                        deadline,
                        created_by,
                        created_by,
                    ),
                )
                result = cur.fetchone()
                penugasan_id = result["id"] if result else None
                log.info(f"Created penugasan: ID={penugasan_id}, joki_id={joki_id}, tanggal={tanggal}")
                return penugasan_id
        except Exception as e:
            log.error(f"Failed to create penugasan: {e}")
            return None

    @staticmethod
    def create_bulk(penugasan_list: List[Dict[str, Any]]) -> int:
        """
        Bulk create multiple penugasan.
        
        Args:
            penugasan_list: List data penugasan
            
        Returns:
            int: Jumlah penugasan yang berhasil dibuat
        """
        success_count = 0
        
        for data in penugasan_list:
            if PortalJokiPenugasanRepository.create(**data):
                success_count += 1
        
        log.info(f"Bulk create penugasan: {success_count}/{len(penugasan_list)} created")
        return success_count

    # ==========================================================
    # UPDATE
    # ==========================================================

    @staticmethod
    def update(
        penugasan_id: int,
        tanggal: date,
        joki_id: int,
        kloter_id: int,
        absen_awal: int,
        absen_akhir: int,
        target_judul: int,
        instruksi: Optional[str] = None,
        deadline: Optional[date] = None,
        updated_by: Optional[str] = None,
    ) -> bool:
        """
        Update penugasan.
        
        Args:
            penugasan_id: ID penugasan
            tanggal: Tanggal penugasan
            joki_id: ID joki
            kloter_id: ID kloter
            absen_awal: Absen awal
            absen_akhir: Absen akhir
            target_judul: Target judul
            instruksi: Instruksi tambahan
            deadline: Deadline
            updated_by: Pengupdate
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Cek konflik absen (exclude current)
            if PortalJokiPenugasanRepository.exists_absen_conflict(
                tanggal, joki_id, absen_awal, absen_akhir, exclude_id=penugasan_id
            ):
                log.warning(f"Absen conflict on update: penugasan_id={penugasan_id}")
                return False
            
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE portal_joki_penugasan
                    SET
                        tanggal = %s,
                        joki_id = %s,
                        kloter_id = %s,
                        absen_awal = %s,
                        absen_akhir = %s,
                        target_judul = %s,
                        instruksi = %s,
                        deadline = %s,
                        updated_by = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        tanggal,
                        joki_id,
                        kloter_id,
                        absen_awal,
                        absen_akhir,
                        target_judul,
                        instruksi,
                        deadline,
                        updated_by,
                        penugasan_id,
                    ),
                )
                affected = cur.rowcount
                log.info(f"Updated penugasan: ID={penugasan_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update penugasan ID {penugasan_id}: {e}")
            return False

    @staticmethod
    def update_status(
        penugasan_id: int,
        status: int,
        updated_by: Optional[str] = None,
    ) -> bool:
        """
        Update status penugasan.
        
        Args:
            penugasan_id: ID penugasan
            status: Status baru
            updated_by: Pengupdate
            
        Returns:
            bool: True jika berhasil
        """
        if status not in PortalJokiPenugasanRepository.STATUS_LABELS:
            log.error(f"Invalid status: {status}")
            return False
        
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE portal_joki_penugasan
                    SET
                        status = %s,
                        updated_by = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (status, updated_by, penugasan_id),
                )
                affected = cur.rowcount
                log.info(f"Updated status penugasan: ID={penugasan_id}, status={status}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update status penugasan ID {penugasan_id}: {e}")
            return False

    @staticmethod
    def update_partial(penugasan_id: int, data: Dict[str, Any]) -> bool:
        """
        Update partial data penugasan.
        
        Args:
            penugasan_id: ID penugasan
            data: Data yang akan diupdate
            
        Returns:
            bool: True jika berhasil
        """
        try:
            allowed_fields = [
                "tanggal", "joki_id", "kloter_id", "absen_awal",
                "absen_akhir", "target_judul", "instruksi", "deadline"
            ]
            updates = []
            params = []
            
            for field in allowed_fields:
                if field in data:
                    updates.append(f"{field} = %s")
                    params.append(data[field])
            
            if not updates:
                log.warning(f"No valid fields to update for penugasan_id: {penugasan_id}")
                return False
            
            updates.append("updated_at = NOW()")
            params.append(penugasan_id)
            
            query = f"UPDATE portal_joki_penugasan SET {', '.join(updates)} WHERE id = %s"
            
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(query, tuple(params))
                affected = cur.rowcount
                log.info(f"Partial update penugasan: ID={penugasan_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to partial update penugasan ID {penugasan_id}: {e}")
            return False

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(penugasan_id: int) -> bool:
        """
        Menghapus penugasan.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_penugasan
                    WHERE id = %s
                    """,
                    (penugasan_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted penugasan: ID={penugasan_id}, affected={affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to delete penugasan ID {penugasan_id}: {e}")
            return False

    @staticmethod
    def delete_by_date(tanggal: date) -> int:
        """
        Menghapus semua penugasan pada tanggal tertentu.
        
        Args:
            tanggal: Tanggal yang akan dihapus
            
        Returns:
            int: Jumlah penugasan yang dihapus
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_penugasan
                    WHERE tanggal = %s
                    """,
                    (tanggal,),
                )
                affected = cur.rowcount
                log.info(f"Deleted penugasan by date: tanggal={tanggal}, affected={affected}")
                return affected
        except Exception as e:
            log.error(f"Failed to delete penugasan by date {tanggal}: {e}")
            return 0

    # ==========================================================
    # VALIDATION / CONFLICT CHECK
    # ==========================================================

    @staticmethod
    def exists_absen_conflict(
        tanggal: date,
        joki_id: int,
        absen_awal: int,
        absen_akhir: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Cek apakah ada konflik absen untuk joki pada tanggal tertentu.
        
        Args:
            tanggal: Tanggal penugasan
            joki_id: ID joki
            absen_awal: Absen awal
            absen_akhir: Absen akhir
            exclude_id: ID penugasan yang dikecualikan (untuk update)
            
        Returns:
            bool: True jika ada konflik
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_penugasan
                WHERE
                    tanggal = %s
                    AND joki_id = %s
                    AND (%s IS NULL OR id <> %s)
                    AND NOT (
                        absen_akhir < %s OR absen_awal > %s
                    )
                LIMIT 1
                """,
                (
                    tanggal,
                    joki_id,
                    exclude_id,
                    exclude_id,
                    absen_awal,
                    absen_akhir,
                ),
            )
            result = cur.fetchone() is not None
            if result:
                log.debug(f"Absen conflict: tanggal={tanggal}, joki_id={joki_id}")
            return result

    @staticmethod
    def exists(penugasan_id: int) -> bool:
        """
        Cek apakah penugasan ada.
        
        Args:
            penugasan_id: ID penugasan
            
        Returns:
            bool: True jika ada
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_penugasan
                WHERE id = %s
                """,
                (penugasan_id,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists: penugasan_id={penugasan_id} -> {result}")
            return result

    @staticmethod
    def exists_on_date(
        joki_id: int,
        tanggal: date,
    ) -> bool:
        """
        Cek apakah joki memiliki penugasan pada tanggal tertentu.
        
        Args:
            joki_id: ID joki
            tanggal: Tanggal yang dicek
            
        Returns:
            bool: True jika ada penugasan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_penugasan
                WHERE joki_id = %s AND tanggal = %s
                LIMIT 1
                """,
                (joki_id, tanggal),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check exists on date: joki_id={joki_id}, tanggal={tanggal} -> {result}")
            return result

    # ==========================================================
    # COUNT
    # ==========================================================

    @staticmethod
    def count(
        status: Optional[int] = None,
        joki_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """
        Menghitung total penugasan dengan filter.
        
        Args:
            status: Filter by status
            joki_id: Filter by joki
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            
        Returns:
            int: Total count
        """
        with get_clean_dict_cursor() as cur:
            query = "SELECT COUNT(*) AS total FROM portal_joki_penugasan WHERE 1=1"
            params = []
            
            if status is not None:
                query += " AND status = %s"
                params.append(status)
            
            if joki_id is not None:
                query += " AND joki_id = %s"
                params.append(joki_id)
            
            if start_date is not None:
                query += " AND tanggal >= %s"
                params.append(start_date)
            
            if end_date is not None:
                query += " AND tanggal <= %s"
                params.append(end_date)
            
            cur.execute(query, tuple(params))
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count penugasan: {total}")
            return total

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

    @staticmethod
    def get_status_label(status: int) -> str:
        """Mendapatkan label status."""
        return PortalJokiPenugasanRepository.STATUS_LABELS.get(status, "Unknown")

    @staticmethod
    def get_status_color(status: int) -> str:
        """Mendapatkan warna status untuk UI."""
        return PortalJokiPenugasanRepository.STATUS_COLORS.get(status, "secondary")

    @staticmethod
    def is_completed(status: int) -> bool:
        """Cek apakah penugasan sudah selesai."""
        return status == PortalJokiPenugasanRepository.STATUS_SELESAI

    @staticmethod
    def is_pending(status: int) -> bool:
        """Cek apakah penugasan masih pending."""
        return status == PortalJokiPenugasanRepository.STATUS_PENDING


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
penugasan_repo = PortalJokiPenugasanRepository()