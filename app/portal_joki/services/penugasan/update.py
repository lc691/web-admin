"""
Portal Joki - Update Penugasan Service

Service untuk mengupdate penugasan.
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime

from app.portal_joki.repositories.auth.auth_repo import (
    PortalJokiAuthRepository,
)
from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.portal_joki.repositories.penugasan.kloter_repo import (
    PortalJokiKloterRepository,
)
from app.portal_joki.repositories.upload.upload_repo import (
    PortalJokiUploadRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class UpdatePenugasanResult:
    """
    Result object untuk update penugasan.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
        changes: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.warnings = warnings or []
        self.changes = changes or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "warnings": self.warnings,
            "changes": self.changes,
        }
    
    @classmethod
    def ok(
        cls,
        message: str = "Penugasan berhasil diperbarui.",
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> "UpdatePenugasanResult":
        """Create success result."""
        return cls(True, message, data or {}, warnings or [], changes or {})
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "UpdatePenugasanResult":
        """Create error result."""
        return cls(False, message, data or {})


# ==========================================================
# UPDATE SERVICE
# ==========================================================
class PortalJokiUpdateService:
    """
    Service Update Penugasan Portal Joki.
    
    Business Flow:
    1. Validasi penugasan exists
    2. Validasi joki (exists & aktif)
    3. Validasi kloter (exists & aktif)
    4. Validasi absen (range, max_absen)
    5. Validasi target (min 1)
    6. Validasi instruksi (not empty)
    7. Validasi deadline (not before tanggal)
    8. Cek bentrok absen (exclude current)
    9. Cek perubahan
    10. Update penugasan
    """

    @staticmethod
    def execute(
        *,
        penugasan_id: int,
        tanggal: date,
        joki_id: int,
        kloter_id: int,
        absen_awal: int,
        absen_akhir: int,
        target_judul: int,
        instruksi: str,
        deadline: Optional[date] = None,
        updated_by: str = "admin",
        skip_conflict_check: bool = False,
    ) -> UpdatePenugasanResult:
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
            instruksi: Instruksi penugasan
            deadline: Deadline (opsional)
            updated_by: Pengupdate (default: admin)
            skip_conflict_check: Skip conflict check (admin override)
            
        Returns:
            UpdatePenugasanResult: Result dengan status
        """
        log.info(f"Update penugasan: ID={penugasan_id}, joki_id={joki_id}, tanggal={tanggal}")

        # ==========================================================
        # 1. CEK PENUGASAN
        # ==========================================================
        try:
            penugasan = PortalJokiPenugasanRepository.get(penugasan_id)
        except Exception as e:
            log.error(f"Failed to get penugasan: {e}")
            return UpdatePenugasanResult.error(f"Gagal mengambil data penugasan: {str(e)}")

        if not penugasan:
            log.warning(f"Penugasan not found: ID={penugasan_id}")
            return UpdatePenugasanResult.error("Penugasan tidak ditemukan.")

        # Cek apakah sudah selesai
        if penugasan.get("status") == 3:
            warnings = ["Penugasan sudah selesai. Perubahan hanya untuk data, status tetap selesai."]
        else:
            warnings = []

        # ==========================================================
        # 2. VALIDASI JOKI
        # ==========================================================
        try:
            joki = PortalJokiAuthRepository.get_by_id(joki_id)
        except Exception as e:
            log.error(f"Failed to get joki: {e}")
            return UpdatePenugasanResult.error(f"Gagal mengambil data joki: {str(e)}")

        if not joki:
            log.warning(f"Joki not found: joki_id={joki_id}")
            return UpdatePenugasanResult.error("Joki tidak ditemukan.")

        if not joki.get("aktif", False):
            log.warning(f"Joki not active: joki_id={joki_id}")
            return UpdatePenugasanResult.error(f"Joki '{joki.get('kode')}' tidak aktif.")

        # ==========================================================
        # 3. VALIDASI KLOTER
        # ==========================================================
        try:
            kloter = PortalJokiKloterRepository.get_by_id(kloter_id)
        except Exception as e:
            log.error(f"Failed to get kloter: {e}")
            return UpdatePenugasanResult.error(f"Gagal mengambil data kloter: {str(e)}")

        if not kloter:
            log.warning(f"Kloter not found: kloter_id={kloter_id}")
            return UpdatePenugasanResult.error("Kloter tidak ditemukan.")

        if not kloter.get("aktif", False):
            log.warning(f"Kloter not active: kloter_id={kloter_id}")
            return UpdatePenugasanResult.error(f"Kloter '{kloter.get('nama')}' tidak aktif.")

        # ==========================================================
        # 4. VALIDASI ABSEN
        # ==========================================================
        max_absen = joki.get("max_absen", 4)

        if absen_awal <= 0:
            return UpdatePenugasanResult.error("Absen awal harus lebih dari 0.")

        if absen_akhir <= 0:
            return UpdatePenugasanResult.error("Absen akhir harus lebih dari 0.")

        if absen_awal > absen_akhir:
            return UpdatePenugasanResult.error("Absen awal harus lebih kecil atau sama dengan absen akhir.")

        if absen_akhir > max_absen:
            return UpdatePenugasanResult.error(
                f"Absen maksimal untuk '{joki.get('kode')}' adalah {max_absen}."
            )

        # ==========================================================
        # 5. VALIDASI TARGET
        # ==========================================================
        if target_judul <= 0:
            return UpdatePenugasanResult.error("Target judul harus lebih dari 0.")

        if target_judul > 50:
            return UpdatePenugasanResult.error("Target judul maksimal 50.")

        # ==========================================================
        # 6. VALIDASI INSTRUKSI
        # ==========================================================
        instruksi = instruksi.strip()

        if not instruksi:
            return UpdatePenugasanResult.error("Instruksi tidak boleh kosong.")

        if len(instruksi) < 10:
            return UpdatePenugasanResult.error("Instruksi minimal 10 karakter.")

        if len(instruksi) > 1000:
            return UpdatePenugasanResult.error("Instruksi maksimal 1000 karakter.")

        # ==========================================================
        # 7. VALIDASI DEADLINE
        # ==========================================================
        if deadline:
            if deadline < tanggal:
                return UpdatePenugasanResult.error(
                    "Deadline tidak boleh sebelum tanggal penugasan."
                )

            max_deadline = tanggal + date.timedelta(days=30)
            if deadline > max_deadline:
                return UpdatePenugasanResult.error(
                    "Deadline maksimal 30 hari dari tanggal penugasan."
                )

        # ==========================================================
        # 8. CEK BENTROK ABSEN
        # ==========================================================
        if not skip_conflict_check:
            try:
                has_conflict = PortalJokiPenugasanRepository.exists_absen_conflict(
                    tanggal=tanggal,
                    joki_id=joki_id,
                    absen_awal=absen_awal,
                    absen_akhir=absen_akhir,
                    exclude_id=penugasan_id,
                )

                if has_conflict:
                    log.warning(f"Absen conflict: joki_id={joki_id}, tanggal={tanggal}")
                    return UpdatePenugasanResult.error(
                        f"Absen {absen_awal}-{absen_akhir} sudah digunakan pada tanggal tersebut."
                    )
            except Exception as e:
                log.error(f"Failed to check conflict: {e}")
                return UpdatePenugasanResult.error(f"Gagal mengecek konflik absen: {str(e)}")

        # ==========================================================
        # 9. CEK PERUBAHAN
        # ==========================================================
        changes = {}
        
        # Compare with current data
        if penugasan.get("tanggal") != tanggal:
            changes["tanggal"] = {"old": penugasan.get("tanggal"), "new": tanggal}
        
        if penugasan.get("joki_id") != joki_id:
            changes["joki_id"] = {"old": penugasan.get("joki_id"), "new": joki_id}
        
        if penugasan.get("kloter_id") != kloter_id:
            changes["kloter_id"] = {"old": penugasan.get("kloter_id"), "new": kloter_id}
        
        if penugasan.get("absen_awal") != absen_awal:
            changes["absen_awal"] = {"old": penugasan.get("absen_awal"), "new": absen_awal}
        
        if penugasan.get("absen_akhir") != absen_akhir:
            changes["absen_akhir"] = {"old": penugasan.get("absen_akhir"), "new": absen_akhir}
        
        if penugasan.get("target_judul") != target_judul:
            changes["target_judul"] = {"old": penugasan.get("target_judul"), "new": target_judul}
        
        if penugasan.get("instruksi") != instruksi:
            changes["instruksi"] = {"old": True, "new": True}  # Just flag that it changed
        
        if penugasan.get("deadline") != deadline:
            changes["deadline"] = {"old": penugasan.get("deadline"), "new": deadline}

        if not changes:
            log.debug(f"No changes for penugasan_id={penugasan_id}")
            return UpdatePenugasanResult.ok(
                "Tidak ada perubahan data.",
                data={"penugasan_id": penugasan_id},
                warnings=warnings,
            )

        # ==========================================================
        # 10. UPDATE
        # ==========================================================
        try:
            success = PortalJokiPenugasanRepository.update(
                penugasan_id=penugasan_id,
                tanggal=tanggal,
                joki_id=joki_id,
                kloter_id=kloter_id,
                absen_awal=absen_awal,
                absen_akhir=absen_akhir,
                target_judul=target_judul,
                instruksi=instruksi,
                deadline=deadline,
                updated_by=updated_by,
            )

            if not success:
                log.error(f"Failed to update penugasan: ID={penugasan_id}")
                return UpdatePenugasanResult.error("Gagal memperbarui penugasan.")

            log.info(f"Penugasan updated: ID={penugasan_id}, changes={len(changes)} fields")

            return UpdatePenugasanResult.ok(
                "Penugasan berhasil diperbarui.",
                data={
                    "penugasan_id": penugasan_id,
                    "joki_kode": joki.get("kode"),
                    "joki_nama": joki.get("nama"),
                    "kloter_nama": kloter.get("nama"),
                    "tanggal": tanggal.isoformat(),
                    "absen": f"{absen_awal}-{absen_akhir}",
                    "target": target_judul,
                    "updated_by": updated_by,
                },
                warnings=warnings,
                changes=changes,
            )

        except Exception as e:
            log.error(f"Failed to update penugasan: {e}")
            return UpdatePenugasanResult.error(f"Gagal memperbarui penugasan: {str(e)}")

    @staticmethod
    def execute_bulk(
        penugasan_list: List[Dict[str, Any]],
        updated_by: str = "admin",
    ) -> Dict[str, Any]:
        """
        Bulk update multiple penugasan.
        
        Args:
            penugasan_list: List data penugasan dengan ID
            updated_by: Pengupdate
            
        Returns:
            dict: Result dengan summary
        """
        log.info(f"Bulk update penugasan: {len(penugasan_list)} items")

        success_count = 0
        failed_count = 0
        updated_ids = []
        errors = []
        total_changes = 0

        for idx, data in enumerate(penugasan_list):
            # Ensure penugasan_id exists
            if "penugasan_id" not in data:
                errors.append({
                    "index": idx,
                    "data": data,
                    "error": "Missing penugasan_id",
                })
                failed_count += 1
                continue

            result = PortalJokiUpdateService.execute(
                **data,
                updated_by=updated_by,
            )

            if result.success:
                success_count += 1
                updated_ids.append(data["penugasan_id"])
                total_changes += len(result.changes)
            else:
                failed_count += 1
                errors.append({
                    "index": idx,
                    "penugasan_id": data.get("penugasan_id"),
                    "error": result.message,
                })

        log.info(f"Bulk update: {success_count} success, {failed_count} failed")

        return {
            "success": failed_count == 0,
            "message": f"{success_count} berhasil diupdate, {failed_count} gagal.",
            "success_count": success_count,
            "failed_count": failed_count,
            "updated_ids": updated_ids,
            "total_changes": total_changes,
            "errors": errors,
        }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
update_service = PortalJokiUpdateService()