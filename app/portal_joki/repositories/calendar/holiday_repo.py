"""
Portal Joki - Holiday Repository

Repository untuk mengelola data hari libur.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.core.database import get_clean_dict_cursor
from app.utils.logger import log


class PortalJokiHolidayRepository:
    """
    Repository Holiday Portal Joki.
    
    Table: portal_joki_holiday
    Columns:
        - id: integer (PK)
        - tanggal: date
        - nama: varchar
        - keterangan: text
        - created_at: timestamp
        - updated_at: timestamp
    """

    # ==========================================================
    # LIST / SELECT
    # ==========================================================

    @staticmethod
    def get_all(
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "tanggal",
        order_dir: str = "ASC",
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua data holiday dengan pagination.
        
        Args:
            limit: Jumlah data per page
            offset: Offset untuk pagination
            order_by: Field untuk sorting
            order_dir: ASC atau DESC
            
        Returns:
            List[dict]: List data holiday
        """
        # Validasi order_by untuk mencegah SQL injection
        allowed_order = ["id", "tanggal", "nama", "created_at"]
        if order_by not in allowed_order:
            order_by = "tanggal"
        
        if order_dir.upper() not in ["ASC", "DESC"]:
            order_dir = "ASC"
        
        with get_clean_dict_cursor() as cur:
            query = """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan,
                    created_at,
                    updated_at
                FROM portal_joki_holiday
                ORDER BY {} {}
            """.format(order_by, order_dir)
            
            params = []
            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
            
            cur.execute(query, tuple(params) if params else None)
            result = cur.fetchall()
            log.debug(f"Get all holidays: {len(result)} rows")
            return result

    @staticmethod
    def get_upcoming(days: int = 30) -> List[Dict[str, Any]]:
        """
        Mendapatkan holiday yang akan datang.
        
        Args:
            days: Jumlah hari ke depan (default 30)
            
        Returns:
            List[dict]: List holiday yang akan datang
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan,
                    EXTRACT(DOW FROM tanggal) AS day_of_week
                FROM portal_joki_holiday
                WHERE tanggal >= CURRENT_DATE
                  AND tanggal <= CURRENT_DATE + INTERVAL '%s days'
                ORDER BY tanggal ASC
                """,
                (days,),
            )
            result = cur.fetchall()
            log.debug(f"Upcoming holidays ({days} days): {len(result)} rows")
            return result

    @staticmethod
    def get_by_year(year: int) -> List[Dict[str, Any]]:
        """
        Mendapatkan holiday berdasarkan tahun.
        
        Args:
            year: Tahun (YYYY)
            
        Returns:
            List[dict]: List holiday di tahun tersebut
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan
                FROM portal_joki_holiday
                WHERE EXTRACT(YEAR FROM tanggal) = %s
                ORDER BY tanggal ASC
                """,
                (year,),
            )
            result = cur.fetchall()
            log.debug(f"Holidays by year {year}: {len(result)} rows")
            return result

    # ==========================================================
    # MONTH
    # ==========================================================

    @staticmethod
    def get_month(
        *,
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan holiday dalam bulan tertentu.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: List holiday di bulan tersebut
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan
                FROM portal_joki_holiday
                WHERE
                    EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                ORDER BY tanggal ASC
                """,
                (tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Holidays month: tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    @staticmethod
    def get_month_with_day_names(
        *,
        tahun: int,
        bulan: int,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan holiday dalam bulan tertentu dengan nama hari.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            List[dict]: List holiday dengan nama hari
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan,
                    TO_CHAR(tanggal, 'Day') AS hari,
                    EXTRACT(DOW FROM tanggal) AS day_of_week
                FROM portal_joki_holiday
                WHERE
                    EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                ORDER BY tanggal ASC
                """,
                (tahun, bulan),
            )
            result = cur.fetchall()
            log.debug(f"Holidays month with day names: tahun={tahun}, bulan={bulan}, rows={len(result)}")
            return result

    # ==========================================================
    # DETAIL
    # ==========================================================

    @staticmethod
    def get(holiday_id: int) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan detail holiday berdasarkan ID.
        
        Args:
            holiday_id: ID holiday
            
        Returns:
            dict: Data holiday atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan,
                    created_at,
                    updated_at
                FROM portal_joki_holiday
                WHERE id = %s
                LIMIT 1
                """,
                (holiday_id,),
            )
            result = cur.fetchone()
            log.debug(f"Get holiday by ID: {holiday_id} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_date(tanggal: date) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan holiday berdasarkan tanggal.
        
        Args:
            tanggal: Tanggal yang dicari
            
        Returns:
            dict: Data holiday atau None jika tidak ditemukan
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan
                FROM portal_joki_holiday
                WHERE tanggal = %s
                LIMIT 1
                """,
                (tanggal,),
            )
            result = cur.fetchone()
            log.debug(f"Get holiday by date: {tanggal} -> {'found' if result else 'not found'}")
            return result

    @staticmethod
    def get_by_date_range(
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Mendapatkan holiday dalam rentang tanggal.
        
        Args:
            start_date: Tanggal awal
            end_date: Tanggal akhir
            
        Returns:
            List[dict]: List holiday dalam rentang
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    tanggal,
                    nama,
                    keterangan
                FROM portal_joki_holiday
                WHERE tanggal BETWEEN %s AND %s
                ORDER BY tanggal ASC
                """,
                (start_date, end_date),
            )
            result = cur.fetchall()
            log.debug(f"Holidays in range: {start_date} - {end_date}, rows={len(result)}")
            return result

    # ==========================================================
    # EXISTS / VALIDATION
    # ==========================================================

    @staticmethod
    def exists(tanggal: date) -> bool:
        """
        Cek apakah tanggal adalah hari libur.
        
        Args:
            tanggal: Tanggal yang dicek
            
        Returns:
            bool: True jika tanggal adalah hari libur
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_holiday
                WHERE tanggal = %s
                LIMIT 1
                """,
                (tanggal,),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check holiday exists: {tanggal} -> {result}")
            return result

    @staticmethod
    def exists_in_month(tahun: int, bulan: int) -> bool:
        """
        Cek apakah ada holiday dalam bulan tertentu.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            bool: True jika ada holiday
        """
        with get_clean_dict_cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM portal_joki_holiday
                WHERE
                    EXTRACT(YEAR FROM tanggal) = %s
                    AND EXTRACT(MONTH FROM tanggal) = %s
                LIMIT 1
                """,
                (tahun, bulan),
            )
            result = cur.fetchone() is not None
            log.debug(f"Check holiday exists in month: tahun={tahun}, bulan={bulan} -> {result}")
            return result

    # ==========================================================
    # COUNT
    # ==========================================================

    @staticmethod
    def count(year: Optional[int] = None) -> int:
        """
        Menghitung total holiday.
        
        Args:
            year: Tahun (opsional)
            
        Returns:
            int: Total count
        """
        with get_clean_dict_cursor() as cur:
            query = "SELECT COUNT(*) AS total FROM portal_joki_holiday"
            params = []
            
            if year is not None:
                query += " WHERE EXTRACT(YEAR FROM tanggal) = %s"
                params.append(year)
            
            cur.execute(query, tuple(params) if params else None)
            result = cur.fetchone()
            total = result["total"] if result else 0
            log.debug(f"Count holidays: {total}" + (f" (year={year})" if year else ""))
            return total

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        *,
        tanggal: date,
        nama: str,
        keterangan: Optional[str] = None,
    ) -> Optional[int]:
        """
        Membuat holiday baru.
        
        Args:
            tanggal: Tanggal libur
            nama: Nama libur
            keterangan: Keterangan tambahan (opsional)
            
        Returns:
            int: ID holiday baru atau None jika gagal
        """
        # Cek duplikat
        if PortalJokiHolidayRepository.exists(tanggal):
            log.warning(f"Holiday already exists for date: {tanggal}")
            return None
        
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    INSERT INTO portal_joki_holiday (
                        tanggal,
                        nama,
                        keterangan,
                        created_at,
                        updated_at
                    ) VALUES (
                        %s, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                    """,
                    (tanggal, nama, keterangan),
                )
                result = cur.fetchone()
                holiday_id = result["id"] if result else None
                log.info(f"Created holiday: {nama} ({tanggal}) ID: {holiday_id}")
                return holiday_id
        except Exception as e:
            log.error(f"Failed to create holiday: {e}")
            return None

    @staticmethod
    def create_bulk(holidays: List[Dict[str, Any]]) -> int:
        """
        Bulk create multiple holidays.
        
        Args:
            holidays: List data holiday [{"tanggal": date, "nama": str, "keterangan": str}]
            
        Returns:
            int: Jumlah holiday yang berhasil dibuat
        """
        success_count = 0
        
        for data in holidays:
            if PortalJokiHolidayRepository.create(**data):
                success_count += 1
        
        log.info(f"Bulk create holidays: {success_count}/{len(holidays)} created")
        return success_count

    # ==========================================================
    # UPDATE
    # ==========================================================

    @staticmethod
    def update(
        *,
        holiday_id: int,
        tanggal: date,
        nama: str,
        keterangan: Optional[str] = None,
    ) -> bool:
        """
        Update data holiday.
        
        Args:
            holiday_id: ID holiday
            tanggal: Tanggal libur
            nama: Nama libur
            keterangan: Keterangan tambahan
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    UPDATE portal_joki_holiday
                    SET
                        tanggal = %s,
                        nama = %s,
                        keterangan = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (tanggal, nama, keterangan, holiday_id),
                )
                affected = cur.rowcount
                log.info(f"Updated holiday ID: {holiday_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to update holiday ID {holiday_id}: {e}")
            return False

    @staticmethod
    def update_partial(
        holiday_id: int,
        data: Dict[str, Any],
    ) -> bool:
        """
        Update partial data holiday.
        
        Args:
            holiday_id: ID holiday
            data: Data yang akan diupdate
            
        Returns:
            bool: True jika berhasil
        """
        try:
            allowed_fields = ["tanggal", "nama", "keterangan"]
            updates = []
            params = []
            
            for field in allowed_fields:
                if field in data:
                    updates.append(f"{field} = %s")
                    params.append(data[field])
            
            if not updates:
                log.warning(f"No valid fields to update for holiday_id: {holiday_id}")
                return False
            
            updates.append("updated_at = NOW()")
            params.append(holiday_id)
            
            query = f"UPDATE portal_joki_holiday SET {', '.join(updates)} WHERE id = %s"
            
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(query, tuple(params))
                affected = cur.rowcount
                log.info(f"Partial update holiday ID: {holiday_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to partial update holiday ID {holiday_id}: {e}")
            return False

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(holiday_id: int) -> bool:
        """
        Menghapus holiday.
        
        Args:
            holiday_id: ID holiday
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_holiday
                    WHERE id = %s
                    """,
                    (holiday_id,),
                )
                affected = cur.rowcount
                log.info(f"Deleted holiday ID: {holiday_id}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to delete holiday ID {holiday_id}: {e}")
            return False

    @staticmethod
    def delete_by_date(tanggal: date) -> bool:
        """
        Menghapus holiday berdasarkan tanggal.
        
        Args:
            tanggal: Tanggal libur
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_holiday
                    WHERE tanggal = %s
                    """,
                    (tanggal,),
                )
                affected = cur.rowcount
                log.info(f"Deleted holiday by date: {tanggal}, affected: {affected}")
                return affected > 0
        except Exception as e:
            log.error(f"Failed to delete holiday by date {tanggal}: {e}")
            return False

    @staticmethod
    def delete_bulk(holiday_ids: List[int]) -> int:
        """
        Bulk delete multiple holidays.
        
        Args:
            holiday_ids: List ID holiday
            
        Returns:
            int: Jumlah holiday yang berhasil dihapus
        """
        if not holiday_ids:
            return 0
        
        try:
            with get_clean_dict_cursor(commit=True) as cur:
                cur.execute(
                    """
                    DELETE FROM portal_joki_holiday
                    WHERE id = ANY(%s)
                    """,
                    (holiday_ids,),
                )
                affected = cur.rowcount
                log.info(f"Bulk delete holidays: {affected} deleted")
                return affected
        except Exception as e:
            log.error(f"Failed to bulk delete holidays: {e}")
            return 0

    # ==========================================================
    # HELPER METHODS
    # ==========================================================

    @staticmethod
    def is_holiday(tanggal: date) -> bool:
        """
        Cek apakah tanggal adalah hari libur (alias untuk exists).
        
        Args:
            tanggal: Tanggal yang dicek
            
        Returns:
            bool: True jika hari libur
        """
        return PortalJokiHolidayRepository.exists(tanggal)

    @staticmethod
    def get_holiday_name(tanggal: date) -> Optional[str]:
        """
        Mendapatkan nama holiday untuk tanggal tertentu.
        
        Args:
            tanggal: Tanggal yang dicari
            
        Returns:
            str: Nama holiday atau None jika bukan hari libur
        """
        holiday = PortalJokiHolidayRepository.get_by_date(tanggal)
        return holiday["nama"] if holiday else None


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
holiday_repo = PortalJokiHolidayRepository()