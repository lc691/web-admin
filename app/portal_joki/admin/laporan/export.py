"""
Portal Joki - Admin Laporan Export Routes
"""

import csv
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, Response

from app.dependencies.auth import require_admin
from app.portal_joki.repositories.laporan.laporan_repo import (
    PortalJokiLaporanRepository,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/export",
    name="portal_joki_admin_laporan_export",
)
async def laporan_export(
    request: Request,
    start_date: str = Query(
        ...,
        description="Tanggal mulai (YYYY-MM-DD)",
    ),
    end_date: str = Query(
        ...,
        description="Tanggal selesai (YYYY-MM-DD)",
    ),
    format: str = Query(
        "csv",
        description="Format export (csv/json)",
    ),
):
    """
    Export laporan.
    """
    log.info(
        f"Export laporan: {start_date} - {end_date}, format={format}"
    )

    try:
        require_admin(request)

        # ==========================================================
        # VALIDASI TANGGAL
        # ==========================================================
        try:
            start = datetime.strptime(
                start_date,
                "%Y-%m-%d",
            ).date()

            end = datetime.strptime(
                end_date,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
                },
                status_code=400,
            )

        # ==========================================================
        # VALIDASI RANGE
        # ==========================================================
        if start > end:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Tanggal mulai tidak boleh lebih besar dari tanggal selesai.",
                },
                status_code=400,
            )

        # ==========================================================
        # AMBIL DATA
        # ==========================================================
        data = PortalJokiLaporanRepository.get_for_export(
            start,
            end,
        )

        # ==========================================================
        # JSON
        # ==========================================================
        if format.lower() == "json":
            return JSONResponse(
                {
                    "success": True,
                    "data": data,
                    "total": len(data),
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )

        # ==========================================================
        # CSV
        # ==========================================================
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "Tanggal",
                "Joki",
                "Kode",
                "Kloter",
                "Absen Awal",
                "Absen Akhir",
                "Target",
                "Status",
                "File",
                "Komentar",
            ]
        )

        status_map = {
            0: "Pending",
            1: "Upload",
            2: "Revisi",
            3: "Selesai",
        }

        for row in data:
            writer.writerow(
                [
                    row.get("tanggal"),
                    row.get("joki_nama"),
                    row.get("joki_kode"),
                    row.get("kloter_nama"),
                    row.get("absen_awal"),
                    row.get("absen_akhir"),
                    row.get("target_judul"),
                    status_map.get(
                        row.get("status"),
                        "Unknown",
                    ),
                    row.get("file_path"),
                    row.get("komentar"),
                ]
            )

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="laporan_{start_date}_{end_date}.csv"'
                )
            },
        )

    except Exception as e:
        log.error(f"Failed to export report: {e}")

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )