"""
Portal Joki - Laporan Constants
"""

# ==========================================================
# DEFAULTS
# ==========================================================

DEFAULT_VIEW = "bulanan"
DEFAULT_EXPORT_FORMAT = "csv"

DEFAULT_MONTHS_TREND = 6
MAX_MONTHS_TREND = 24
MIN_MONTHS_TREND = 1


# ==========================================================
# MONTHS
# ==========================================================

MONTH_NAMES = (
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
)


# ==========================================================
# STATUS
# ==========================================================

STATUS_PENDING = 0
STATUS_UPLOAD = 1
STATUS_REVISI = 2
STATUS_SELESAI = 3

STATUS_LABELS = {
    STATUS_PENDING: "Pending",
    STATUS_UPLOAD: "Upload",
    STATUS_REVISI: "Revisi",
    STATUS_SELESAI: "Selesai",
}

STATUS_COLORS = {
    STATUS_PENDING: "warning",
    STATUS_UPLOAD: "info",
    STATUS_REVISI: "danger",
    STATUS_SELESAI: "success",
}


# ==========================================================
# VIEW
# ==========================================================

VIEW_BULANAN = "bulanan"
VIEW_HARIAN = "harian"
VIEW_STATISTIK = "statistik"

VALID_VIEWS = (
    VIEW_BULANAN,
    VIEW_HARIAN,
    VIEW_STATISTIK,
)


# ==========================================================
# EXPORT
# ==========================================================

EXPORT_FORMAT_CSV = "csv"
EXPORT_FORMAT_JSON = "json"

VALID_EXPORT_FORMATS = (
    EXPORT_FORMAT_CSV,
    EXPORT_FORMAT_JSON,
)

EXPORT_HEADERS = (
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
)