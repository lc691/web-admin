import asyncio
import time

from configs.logging_setup import log
from db.connect import get_dict_cursor

# =====================================================
# CACHE GLOBAL
# =====================================================
_trusted_ips_cache: set[str] = set()
_last_load_time: float = 0.0
CACHE_TTL = 300  # detik
_lock = asyncio.Lock()

DEFAULT_TRUSTED_IPS = {
    "100.64.0.9",
    "103.123.45.68",
}


async def load_trusted_ips() -> set[str]:
    """
    Load daftar IP terpercaya dari DB dengan TTL cache.
    Tidak perlu restart service jika data DB berubah.
    """
    global _trusted_ips_cache, _last_load_time

    now = time.monotonic()
    if now - _last_load_time < CACHE_TTL and _trusted_ips_cache:
        return _trusted_ips_cache

    async with _lock:
        now = time.monotonic()
        if now - _last_load_time < CACHE_TTL and _trusted_ips_cache:
            return _trusted_ips_cache

        try:
            with get_dict_cursor() as (cursor, _):
                cursor.execute("SELECT ip FROM trusted_ips")
                rows = cursor.fetchall()

                _trusted_ips_cache = {r["ip"] for r in rows}
                _last_load_time = now

                log.info(
                    "[WEBHOOK] Trusted IPs refreshed count=%s",
                    len(_trusted_ips_cache),
                )

        except Exception as e:
            log.error("[WEBHOOK] Gagal load trusted IPs dari DB: %s", e)

            if not _trusted_ips_cache:
                _trusted_ips_cache = DEFAULT_TRUSTED_IPS.copy()
                log.warning(
                    "[WEBHOOK] Using fallback trusted IPs count=%s",
                    len(_trusted_ips_cache),
                )

    return _trusted_ips_cache


def invalidate_trusted_ip_cache():
    """
    Paksa cache trusted IP di-refresh pada request berikutnya.
    Dipanggil setelah admin panel INSERT / UPDATE / DELETE.
    """
    global _last_load_time
    _last_load_time = 0
