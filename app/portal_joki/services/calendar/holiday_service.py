"""
Portal Joki - Holiday Service

Service untuk manajemen hari libur portal joki.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime

from app.portal_joki.repositories.calendar.holiday_repo import (
    PortalJokiHolidayRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class HolidayResult:
    """
    Result object untuk operasi holiday.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Any = None,
        errors: Optional[List[str]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data
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
    def ok(cls, message: str = "OK", data: Any = None) -> "HolidayResult":
        """Create success result."""
        return cls(True, message, data)
    
    @classmethod
    def error(cls, message: str, errors: Optional[List[str]] = None) -> "HolidayResult":
        """Create error result."""
        return cls(False, message, None, errors or [])


# ==========================================================
# HOLIDAY SERVICE
# ==========================================================
class PortalJokiHolidayService:
    """
    Service Holiday Portal Joki.
    
    Menyediakan fungsi untuk:
    - List semua holiday
    - List holiday per bulan
    - Detail holiday
    - Create holiday
    - Update holiday
    - Delete holiday
    - Check holiday
    - Bulk operations
    """

    # ==========================================================
    # LIST
    # ==========================================================

    @staticmethod
    def all(
        limit: Optional[int] = None,
        offset: int = 0,
        year: Optional[int] = None,
    ) -> HolidayResult:
        """
        Mendapatkan semua data holiday.
        
        Args:
            limit: Jumlah data per page
            offset: Offset untuk pagination
            year: Filter by tahun (opsional)
            
        Returns:
            HolidayResult: Result dengan data holiday
        """
        log.info(f"Get all holidays: limit={limit}, offset={offset}, year={year}")
        
        try:
            if year:
                data = PortalJokiHolidayRepository.get_by_year(year)
            else:
                data = PortalJokiHolidayRepository.get_all(
                    limit=limit,
                    offset=offset,
                )
            
            total = PortalJokiHolidayRepository.count(year=year)
            
            log.debug(f"Get all holidays: {len(data)} rows, total={total}")
            
            return HolidayResult.ok(
                "OK",
                {
                    "data": data,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            )
        except Exception as e:
            log.error(f"Failed to get holidays: {e}")
            return HolidayResult.error(f"Gagal mengambil data holiday: {str(e)}")

    # ==========================================================
    # MONTH
    # ==========================================================

    @staticmethod
    def month(
        *,
        tahun: int,
        bulan: int,
    ) -> HolidayResult:
        """
        Mendapatkan holiday dalam bulan tertentu.
        
        Args:
            tahun: Tahun (YYYY)
            bulan: Bulan (1-12)
            
        Returns:
            HolidayResult: Result dengan data holiday
        """
        # Validasi bulan
        if bulan < 1 or bulan > 12:
            log.warning(f"Invalid month: {bulan}")
            return HolidayResult.error("Bulan tidak valid. (1-12)")
        
        log.info(f"Get holidays month: tahun={tahun}, bulan={bulan}")
        
        try:
            data = PortalJokiHolidayRepository.get_month(
                tahun=tahun,
                bulan=bulan,
            )
            
            # Get with day names
            data_with_day = PortalJokiHolidayRepository.get_month_with_day_names(
                tahun=tahun,
                bulan=bulan,
            )
            
            log.debug(f"Get month holidays: {len(data)} rows")
            
            return HolidayResult.ok(
                "OK",
                {
                    "tahun": tahun,
                    "bulan": bulan,
                    "data": data,
                    "data_with_day": data_with_day,
                    "total": len(data),
                }
            )
        except Exception as e:
            log.error(f"Failed to get month holidays: {e}")
            return HolidayResult.error(f"Gagal mengambil data holiday: {str(e)}")

    # ==========================================================
    # DETAIL
    # ==========================================================

    @staticmethod
    def detail(holiday_id: int) -> HolidayResult:
        """
        Mendapatkan detail holiday berdasarkan ID.
        
        Args:
            holiday_id: ID holiday
            
        Returns:
            HolidayResult: Result dengan data holiday
        """
        log.info(f"Get holiday detail: holiday_id={holiday_id}")
        
        try:
            data = PortalJokiHolidayRepository.get(holiday_id)
            
            if not data:
                log.warning(f"Holiday not found: holiday_id={holiday_id}")
                return HolidayResult.error("Hari libur tidak ditemukan.")
            
            log.debug(f"Holiday detail found: {data.get('nama')}")
            
            return HolidayResult.ok("OK", data)
        except Exception as e:
            log.error(f"Failed to get holiday detail: {e}")
            return HolidayResult.error(f"Gagal mengambil data holiday: {str(e)}")

    # ==========================================================
    # BY DATE
    # ==========================================================

    @staticmethod
    def by_date(tanggal: date) -> HolidayResult:
        """
        Mendapatkan holiday berdasarkan tanggal.
        
        Args:
            tanggal: Tanggal yang dicari
            
        Returns:
            HolidayResult: Result dengan data holiday
        """
        log.info(f"Get holiday by date: {tanggal}")
        
        try:
            data = PortalJokiHolidayRepository.get_by_date(tanggal)
            
            if not data:
                log.debug(f"No holiday on {tanggal}")
                return HolidayResult.ok(
                    "Bukan hari libur.",
                    {"tanggal": tanggal.isoformat(), "is_holiday": False}
                )
            
            log.debug(f"Holiday found on {tanggal}: {data.get('nama')}")
            
            return HolidayResult.ok(
                "Hari libur.",
                {
                    "tanggal": tanggal.isoformat(),
                    "is_holiday": True,
                    "data": data,
                }
            )
        except Exception as e:
            log.error(f"Failed to get holiday by date: {e}")
            return HolidayResult.error(f"Gagal mengambil data holiday: {str(e)}")

    # ==========================================================
    # CHECK HOLIDAY
    # ==========================================================

    @staticmethod
    def is_holiday(tanggal: date) -> bool:
        """
        Cek apakah tanggal adalah hari libur.
        
        Args:
            tanggal: Tanggal yang dicek
            
        Returns:
            bool: True jika hari libur
        """
        try:
            result = PortalJokiHolidayRepository.is_holiday(tanggal)
            log.debug(f"Is holiday: {tanggal} -> {result}")
            return result
        except Exception as e:
            log.error(f"Failed to check holiday: {e}")
            return False

    # ==========================================================
    # CREATE
    # ==========================================================

    @staticmethod
    def create(
        *,
        tanggal: date,
        nama: str,
        keterangan: Optional[str] = None,
    ) -> HolidayResult:
        """
        Membuat holiday baru.
        
        Args:
            tanggal: Tanggal libur
            nama: Nama libur
            keterangan: Keterangan tambahan
            
        Returns:
            HolidayResult: Result dengan ID holiday
        """
        nama = nama.strip()
        
        log.info(f"Create holiday: {nama} ({tanggal})")
        
        # ==========================================================
        # 1. Validasi
        # ==========================================================
        if not nama:
            return HolidayResult.error("Nama hari libur wajib diisi.")
        
        if len(nama) < 3:
            return HolidayResult.error("Nama hari libur minimal 3 karakter.")
        
        # Cek duplikat
        try:
            if PortalJokiHolidayRepository.exists(tanggal):
                log.warning(f"Holiday already exists on {tanggal}")
                return HolidayResult.error(f"Tanggal {tanggal} sudah menjadi hari libur.")
        except Exception as e:
            log.error(f"Failed to check holiday exists: {e}")
            return HolidayResult.error(f"Gagal mengecek duplikat: {str(e)}")
        
        # ==========================================================
        # 2. Create
        # ==========================================================
        try:
            holiday_id = PortalJokiHolidayRepository.create(
                tanggal=tanggal,
                nama=nama,
                keterangan=keterangan,
            )
            
            if not holiday_id:
                return HolidayResult.error("Gagal menambahkan hari libur.")
            
            log.info(f"Holiday created: ID={holiday_id}, {nama} ({tanggal})")
            
            return HolidayResult.ok(
                "Hari libur berhasil ditambahkan.",
                {
                    "id": holiday_id,
                    "tanggal": tanggal.isoformat(),
                    "nama": nama,
                }
            )
        except Exception as e:
            log.error(f"Failed to create holiday: {e}")
            return HolidayResult.error(f"Gagal menambahkan hari libur: {str(e)}")

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
    ) -> HolidayResult:
        """
        Update holiday.
        
        Args:
            holiday_id: ID holiday
            tanggal: Tanggal libur baru
            nama: Nama libur baru
            keterangan: Keterangan baru
            
        Returns:
            HolidayResult: Result status
        """
        nama = nama.strip()
        
        log.info(f"Update holiday: ID={holiday_id}, {nama} ({tanggal})")
        
        # ==========================================================
        # 1. Validasi existence
        # ==========================================================
        try:
            holiday = PortalJokiHolidayRepository.get(holiday_id)
            
            if not holiday:
                log.warning(f"Holiday not found: ID={holiday_id}")
                return HolidayResult.error("Hari libur tidak ditemukan.")
        except Exception as e:
            log.error(f"Failed to get holiday: {e}")
            return HolidayResult.error(f"Gagal mengambil data holiday: {str(e)}")
        
        # ==========================================================
        # 2. Validasi nama
        # ==========================================================
        if not nama:
            return HolidayResult.error("Nama hari libur wajib diisi.")
        
        if len(nama) < 3:
            return HolidayResult.error("Nama hari libur minimal 3 karakter.")
        
        # ==========================================================
        # 3. Validasi duplikat (jika tanggal berubah)
        # ==========================================================
        try:
            if holiday["tanggal"] != tanggal:
                if PortalJokiHolidayRepository.exists(tanggal):
                    log.warning(f"Holiday already exists on {tanggal}")
                    return HolidayResult.error(f"Tanggal {tanggal} sudah menjadi hari libur.")
        except Exception as e:
            log.error(f"Failed to check holiday exists: {e}")
            return HolidayResult.error(f"Gagal mengecek duplikat: {str(e)}")
        
        # ==========================================================
        # 4. Update
        # ==========================================================
        try:
            success = PortalJokiHolidayRepository.update(
                holiday_id=holiday_id,
                tanggal=tanggal,
                nama=nama,
                keterangan=keterangan,
            )
            
            if not success:
                return HolidayResult.error("Gagal memperbarui hari libur.")
            
            log.info(f"Holiday updated: ID={holiday_id}")
            
            return HolidayResult.ok(
                "Hari libur berhasil diperbarui.",
                {
                    "id": holiday_id,
                    "tanggal": tanggal.isoformat(),
                    "nama": nama,
                }
            )
        except Exception as e:
            log.error(f"Failed to update holiday: {e}")
            return HolidayResult.error(f"Gagal memperbarui hari libur: {str(e)}")

    # ==========================================================
    # DELETE
    # ==========================================================

    @staticmethod
    def delete(holiday_id: int) -> HolidayResult:
        """
        Delete holiday.
        
        Args:
            holiday_id: ID holiday
            
        Returns:
            HolidayResult: Result status
        """
        log.info(f"Delete holiday: ID={holiday_id}")
        
        # ==========================================================
        # 1. Validasi existence
        # ==========================================================
        try:
            holiday = PortalJokiHolidayRepository.get(holiday_id)
            
            if not holiday:
                log.warning(f"Holiday not found: ID={holiday_id}")
                return HolidayResult.error("Hari libur tidak ditemukan.")
        except Exception as e:
            log.error(f"Failed to get holiday: {e}")
            return HolidayResult.error(f"Gagal mengambil data holiday: {str(e)}")
        
        # ==========================================================
        # 2. Delete
        # ==========================================================
        try:
            success = PortalJokiHolidayRepository.delete(holiday_id)
            
            if not success:
                return HolidayResult.error("Gagal menghapus hari libur.")
            
            log.info(f"Holiday deleted: ID={holiday_id}, {holiday.get('nama')} ({holiday.get('tanggal')})")
            
            return HolidayResult.ok(
                "Hari libur berhasil dihapus.",
                {
                    "id": holiday_id,
                    "tanggal": holiday.get("tanggal").isoformat() if holiday.get("tanggal") else None,
                    "nama": holiday.get("nama"),
                }
            )
        except Exception as e:
            log.error(f"Failed to delete holiday: {e}")
            return HolidayResult.error(f"Gagal menghapus hari libur: {str(e)}")

    # ==========================================================
    # BULK OPERATIONS
    # ==========================================================

    @staticmethod
    def create_bulk(
        holidays: List[Dict[str, Any]],
    ) -> HolidayResult:
        """
        Bulk create holidays.
        
        Args:
            holidays: List data holiday [{"tanggal": date, "nama": str, "keterangan": str}]
            
        Returns:
            HolidayResult: Result dengan jumlah sukses
        """
        log.info(f"Bulk create holidays: {len(holidays)} items")
        
        success_count = 0
        errors = []
        
        for idx, data in enumerate(holidays):
            try:
                result = PortalJokiHolidayService.create(**data)
                if result.success:
                    success_count += 1
                else:
                    errors.append(f"Item {idx+1}: {result.message}")
            except Exception as e:
                errors.append(f"Item {idx+1}: {str(e)}")
        
        log.info(f"Bulk create holidays: {success_count}/{len(holidays)} success")
        
        if success_count == len(holidays):
            return HolidayResult.ok(
                f"Semua {success_count} hari libur berhasil ditambahkan.",
                {"success_count": success_count, "total": len(holidays)}
            )
        else:
            return HolidayResult(
                False,
                f"{success_count} dari {len(holidays)} hari libur berhasil ditambahkan.",
                {"success_count": success_count, "total": len(holidays)},
                errors,
            )

    @staticmethod
    def delete_bulk(holiday_ids: List[int]) -> HolidayResult:
        """
        Bulk delete holidays.
        
        Args:
            holiday_ids: List ID holiday
            
        Returns:
            HolidayResult: Result dengan jumlah sukses
        """
        log.info(f"Bulk delete holidays: {len(holiday_ids)} items")
        
        success_count = 0
        errors = []
        
        for holiday_id in holiday_ids:
            try:
                result = PortalJokiHolidayService.delete(holiday_id)
                if result.success:
                    success_count += 1
                else:
                    errors.append(f"ID {holiday_id}: {result.message}")
            except Exception as e:
                errors.append(f"ID {holiday_id}: {str(e)}")
        
        log.info(f"Bulk delete holidays: {success_count}/{len(holiday_ids)} success")
        
        if success_count == len(holiday_ids):
            return HolidayResult.ok(
                f"Semua {success_count} hari libur berhasil dihapus.",
                {"success_count": success_count, "total": len(holiday_ids)}
            )
        else:
            return HolidayResult(
                False,
                f"{success_count} dari {len(holiday_ids)} hari libur berhasil dihapus.",
                {"success_count": success_count, "total": len(holiday_ids)},
                errors,
            )

    # ==========================================================
    # UPCOMING HOLIDAYS
    # ==========================================================

    @staticmethod
    def upcoming(days: int = 30) -> HolidayResult:
        """
        Mendapatkan holiday yang akan datang.
        
        Args:
            days: Jumlah hari ke depan
            
        Returns:
            HolidayResult: Result dengan data upcoming holidays
        """
        log.info(f"Get upcoming holidays: {days} days")
        
        try:
            data = PortalJokiHolidayRepository.get_upcoming(days)
            
            log.debug(f"Upcoming holidays: {len(data)} rows")
            
            return HolidayResult.ok(
                "OK",
                {
                    "days": days,
                    "data": data,
                    "total": len(data),
                }
            )
        except Exception as e:
            log.error(f"Failed to get upcoming holidays: {e}")
            return HolidayResult.error(f"Gagal mengambil data upcoming: {str(e)}")


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
holiday_service = PortalJokiHolidayService()