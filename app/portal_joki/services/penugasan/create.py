"""
Portal Joki - Create Penugasan Service

Service untuk membuat penugasan baru.
"""

from typing import Optional, Dict, Any
from datetime import date, datetime

from app.portal_joki.repositories.auth.auth_repo import PortalJokiAuthRepository
from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.portal_joki.repositories.penugasan.kloter_repo import (
    PortalJokiKloterRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class CreatePenugasanResult:
    """
    Result object untuk create penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        penugasan_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[list] = None,
    ):
        self.success = success
        self.message = message
        self.penugasan_id = penugasan_id
        self.data = data or {}
        self.errors = errors or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "penugasan_id": self.penugasan_id,
            "data": self.data,
            "errors": self.errors,
        }
    
    @classmethod
    def ok(
        cls,
        penugasan_id: int,
        message: str = "Penugasan berhasil dibuat.",
        data: Optional[Dict[str, Any]] = None,
    ) -> "CreatePenugasanResult":
        """Create success result."""
        return cls(True, message, penugasan_id, data or {})
    
    @classmethod
    def error(
        cls,
        message: str,
        errors: Optional[list] = None,
    ) -> "CreatePenugasanResult":
        """Create error result."""
        return cls(False, message, None, {}, errors or [])


# ==========================================================
# CREATE SERVICE
# ==========================================================
class PortalJokiCreateService:
    """
    Service Create Penugasan Portal Joki.
    
    Business Flow:
    1. Validasi joki (exists & aktif)
    2. Validasi kloter (exists & aktif)
    3. Validasi absen (range, max_absen)
    4. Validasi target (min 1)
    5. Validasi instruksi (not empty)
    6. Validasi deadline (not before tanggal)
    7. Cek bentrok absen
    8. Create penugasan
    """

    @staticmethod
    def execute(
        *,
        tanggal: date,
        joki_id: int,
        kloter_id: int,
        absen_awal: int,
        absen_akhir: int,
        target_judul: int,
        instruksi: str,
        deadline: Optional[date] = None,
        created_by: str = "admin",
        skip_conflict_check: bool = False,
    ) -> CreatePenugasanResult:
        """
        Create new penugasan.
        
        Args:
            tanggal: Tanggal penugasan
            joki_id: ID joki
            kloter_id: ID kloter
            absen_awal: Absen awal
            absen_akhir: Absen akhir
            target_judul: Target judul
            instruksi: Instruksi penugasan
            deadline: Deadline (opsional)
            created_by: Pembuat (default: admin)
            skip_conflict_check: Skip conflict check (admin override)
            
        Returns:
            CreatePenugasanResult: Result dengan ID penugasan
        """
        log.info(f"Create penugasan: joki_id={joki_id}, tanggal={tanggal}, kloter_id={kloter_id}")
        
        # ==========================================================
        # 1. VALIDASI JOKI
        # ==========================================================
        try:
            joki = PortalJokiAuthRepository.get_by_id(joki_id)
        except Exception as e:
            log.error(f"Failed to get joki: {e}")
            return CreatePenugasanResult.error(f"Gagal mengambil data joki: {str(e)}")
        
        if not joki:
            log.warning(f"Joki not found: joki_id={joki_id}")
            return CreatePenugasanResult.error("Joki tidak ditemukan.")
        
        if not joki.get("aktif", False):
            log.warning(f"Joki not active: joki_id={joki_id}")
            return CreatePenugasanResult.error(f"Joki '{joki.get('kode')}' tidak aktif.")

        # ==========================================================
        # 2. VALIDASI KLOTER
        # ==========================================================
        try:
            kloter = PortalJokiKloterRepository.get_by_id(kloter_id)
        except Exception as e:
            log.error(f"Failed to get kloter: {e}")
            return CreatePenugasanResult.error(f"Gagal mengambil data kloter: {str(e)}")
        
        if not kloter:
            log.warning(f"Kloter not found: kloter_id={kloter_id}")
            return CreatePenugasanResult.error("Kloter tidak ditemukan.")
        
        if not kloter.get("aktif", False):
            log.warning(f"Kloter not active: kloter_id={kloter_id}")
            return CreatePenugasanResult.error(f"Kloter '{kloter.get('nama')}' tidak aktif.")

        # ==========================================================
        # 3. VALIDASI ABSEN
        # ==========================================================
        max_absen = joki.get("max_absen", 4)
        
        if absen_awal <= 0:
            return CreatePenugasanResult.error("Absen awal harus lebih dari 0.")
        
        if absen_akhir <= 0:
            return CreatePenugasanResult.error("Absen akhir harus lebih dari 0.")
        
        if absen_awal > absen_akhir:
            return CreatePenugasanResult.error("Absen awal harus lebih kecil atau sama dengan absen akhir.")
        
        if absen_akhir > max_absen:
            return CreatePenugasanResult.error(
                f"Absen maksimal untuk '{joki.get('kode')}' adalah {max_absen}."
            )

        # ==========================================================
        # 4. VALIDASI TARGET
        # ==========================================================
        if target_judul <= 0:
            return CreatePenugasanResult.error("Target judul harus lebih dari 0.")
        
        if target_judul > 50:
            return CreatePenugasanResult.error("Target judul maksimal 50.")

        # ==========================================================
        # 5. VALIDASI INSTRUKSI
        # ==========================================================
        instruksi = instruksi.strip()
        
        if not instruksi:
            return CreatePenugasanResult.error("Instruksi tidak boleh kosong.")
        
        if len(instruksi) < 10:
            return CreatePenugasanResult.error("Instruksi minimal 10 karakter.")
        
        if len(instruksi) > 1000:
            return CreatePenugasanResult.error("Instruksi maksimal 1000 karakter.")

        # ==========================================================
        # 6. VALIDASI DEADLINE
        # ==========================================================
        if deadline:
            if deadline < tanggal:
                return CreatePenugasanResult.error(
                    "Deadline tidak boleh sebelum tanggal penugasan."
                )
            
            # Deadline max 30 days ahead
            max_deadline = tanggal + date.timedelta(days=30)
            if deadline > max_deadline:
                return CreatePenugasanResult.error(
                    "Deadline maksimal 30 hari dari tanggal penugasan."
                )

        # ==========================================================
        # 7. CEK BENTROK ABSEN
        # ==========================================================
        if not skip_conflict_check:
            try:
                has_conflict = PortalJokiPenugasanRepository.exists_absen_conflict(
                    tanggal=tanggal,
                    joki_id=joki_id,
                    absen_awal=absen_awal,
                    absen_akhir=absen_akhir,
                )
                
                if has_conflict:
                    log.warning(f"Absen conflict: joki_id={joki_id}, tanggal={tanggal}")
                    return CreatePenugasanResult.error(
                        f"Absen {absen_awal}-{absen_akhir} sudah digunakan pada tanggal tersebut."
                    )
            except Exception as e:
                log.error(f"Failed to check conflict: {e}")
                return CreatePenugasanResult.error(f"Gagal mengecek konflik absen: {str(e)}")

        # ==========================================================
        # 8. SIMPAN
        # ==========================================================
        try:
            penugasan_id = PortalJokiPenugasanRepository.create(
                tanggal=tanggal,
                joki_id=joki_id,
                kloter_id=kloter_id,
                absen_awal=absen_awal,
                absen_akhir=absen_akhir,
                target_judul=target_judul,
                instruksi=instruksi,
                deadline=deadline,
                created_by=created_by,
            )
            
            if not penugasan_id:
                log.error(f"Failed to create penugasan: unknown error")
                return CreatePenugasanResult.error("Gagal membuat penugasan.")
            
            log.info(f"Penugasan created: ID={penugasan_id}, joki={joki.get('kode')}, tanggal={tanggal}")
            
            return CreatePenugasanResult.ok(
                penugasan_id,
                "Penugasan berhasil dibuat.",
                {
                    "joki_kode": joki.get("kode"),
                    "joki_nama": joki.get("nama"),
                    "kloter_nama": kloter.get("nama"),
                    "tanggal": tanggal.isoformat(),
                    "absen": f"{absen_awal}-{absen_akhir}",
                    "target": target_judul,
                }
            )
            
        except Exception as e:
            log.error(f"Failed to create penugasan: {e}")
            return CreatePenugasanResult.error(f"Gagal membuat penugasan: {str(e)}")

    @staticmethod
    def execute_bulk(
        penugasan_list: list,
        created_by: str = "admin",
    ) -> Dict[str, Any]:
        """
        Bulk create multiple penugasan.
        
        Args:
            penugasan_list: List data penugasan
            created_by: Pembuat
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk create penugasan: {len(penugasan_list)} items")
        
        success_count = 0
        failed_count = 0
        created_ids = []
        errors = []
        
        for idx, data in enumerate(penugasan_list):
            result = PortalJokiCreateService.execute(
                **data,
                created_by=created_by,
            )
            
            if result.success:
                success_count += 1
                created_ids.append(result.penugasan_id)
            else:
                failed_count += 1
                errors.append({
                    "index": idx,
                    "data": data,
                    "error": result.message,
                })
        
        log.info(f"Bulk create: {success_count} success, {failed_count} failed")
        
        return {
            "success": failed_count == 0,
            "message": f"{success_count} berhasil, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "created_ids": created_ids,
            "errors": errors,
        }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
create_service = PortalJokiCreateService()