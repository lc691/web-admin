"""
Routes Configuration - Standardized Router Registration
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.utils.logger import log


# ================================
# ROUTER REGISTRY
# ================================
class RouterRegistry:
    """
    Registry pattern untuk mengelola semua router.
    Memudahkan penambahan, penghapusan, dan tracking router.
    """
    
    def __init__(self):
        self._routers = []
        self._router_count = 0
    
    def register(self, router, prefix: str = None, tags: list = None):
        """Register a router dengan metadata"""
        self._routers.append({
            "router": router,
            "prefix": prefix,
            "tags": tags or []
        })
        self._router_count += 1
        return self
    
    def apply_to_app(self, app: FastAPI):
        """Apply all registered routers ke FastAPI app"""
        for item in self._routers:
            router = item["router"]
            prefix = item["prefix"]
            tags = item["tags"]
            
            if prefix:
                app.include_router(router, prefix=prefix, tags=tags)
            else:
                app.include_router(router, tags=tags)
            
            log.debug(f"   ✅ Router registered: {router.__class__.__name__ if hasattr(router, '__class__') else router.prefix if hasattr(router, 'prefix') else 'Unknown'}")
        
        log.info(f"✅ Registered {self._router_count} routers")
        return app


# ================================
# ROUTER DEFINITIONS
# ================================

def get_routers() -> list:
    """
    Return list of (router, prefix, tags) tuples.
    Semua router didefinisikan di sini secara terpusat.
    """
    
    # ================================
    # 1. AUTH & USERS
    # ================================
    from app.routers.auth import router as auth_router
    from app.users.routes import router as user_router
    from app.admins.routes import router as admins_router
    
    # ================================
    # 2. VIP MODULE
    # ================================
    from app.vip_users.routes import router as vip_user_router
    from app.vip_logs.routes import router as vip_logs_router
    from app.vip_packages.routes import router as vip_packages_router
    from app.vip_vouchers.routes import router as vip_vouchers_router
    
    # ================================
    # 3. FINANCIAL
    # ================================
    from app.donation_logs.routes import router as donation_logs_router
    from app.referrals.routes import router as referral_router
    from app.affiliate.routes import router as affiliate_router
    from app.affiliate.router_payout import router as affiliate_payout_router
    
    # ================================
    # 4. CHANNELS
    # ================================
    from app.channel.channel_posting.routes import router as channel_router
    from app.channel.channel_required.routes import router as required_channel_router
    
    # ================================
    # 5. CONTENT
    # ================================
    from app.routers.files import router as files_router
    from app.routers.show_files import router as show_files_router
    from app.shows.routes import router as shows_router
    
    # ================================
    # 6. SECURITY & PLATFORM
    # ================================
    from app.trust_ip.routes import router as trust_ip_router
    from app.platform.routes import router as platform_router
    
    # ================================
    # 7. SOUNDON / MUSIC
    # ================================
    from app.music.channels.page import router as channels_page_router
    from app.music.channels.router import router as channels_api_router
    from app.music.artists import artists
    from app.music.songs.page import router as songs_page_router
    from app.music.songs.router import router as songs_api_router
    from app.routes.channel_blacklists import router as blacklist_router
    
    # ================================
    # 8. JOKI / CATATAN
    # ================================
    from app.joki.joki import router as joki_router
    from app.joki.kloter import router as kloter_router
    from app.joki.catatan import router as catatan_router
    from app.joki.rekap import router as rekap_router
    from app.joki.laporan import router as laporan_router
    from app.joki.dashboard import router as dashboard_lapor
    from app.portal_joki.admin import router as portal_joki_admin_router
    
    # ================================
    # 9. DASHBOARD
    # ================================
    from app.api.dashboard import router as dashboard_router
    
    # ================================
    # RETURN ALL ROUTERS
    # ================================
    return [
        # ===== AUTH & USERS =====
        (auth_router, None, ["auth"]),
        (user_router, None, ["users"]),
        (admins_router, None, ["admins"]),
        
        # ===== VIP MODULE =====
        (vip_user_router, None, ["vip"]),
        (vip_logs_router, None, ["vip", "logs"]),
        (vip_packages_router, None, ["vip", "packages"]),
        (vip_vouchers_router, None, ["vip", "vouchers"]),
        
        # ===== FINANCIAL =====
        (donation_logs_router, None, ["financial", "donation"]),
        (referral_router, None, ["financial", "referral"]),
        (affiliate_router, None, ["financial", "affiliate"]),
        (affiliate_payout_router, None, ["financial", "affiliate"]),
        
        # ===== CHANNELS =====
        (channel_router, None, ["channels"]),
        (required_channel_router, None, ["channels", "required"]),
        
        # ===== CONTENT =====
        (files_router, None, ["content", "files"]),
        (show_files_router, None, ["content", "show"]),
        (shows_router, None, ["content", "shows"]),
        
        # ===== SECURITY & PLATFORM =====
        (trust_ip_router, None, ["security"]),
        (platform_router, None, ["platform"]),
        
        # ===== SOUNDON =====
        (artists.router, None, ["soundon", "artists"]),
        (channels_page_router, None, ["soundon", "channels"]),
        (channels_api_router, "/api", ["soundon", "channels"]),
        (songs_page_router, None, ["soundon", "songs"]),
        (songs_api_router, "/api", ["soundon", "songs"]),
        (blacklist_router, None, ["soundon", "blacklist"]),
        
        # ===== JOKI =====
        (joki_router, None, ["joki"]),
        (kloter_router, None, ["joki", "kloter"]),
        (catatan_router, None, ["joki", "catatan"]),
        (rekap_router, None, ["joki", "rekap"]),
        (laporan_router, None, ["joki", "laporan"]),
        (dashboard_lapor, None, ["joki", "dashboard"]),
        (portal_joki_admin_router, None, ["joki", "admin"]),
        
        # ===== DASHBOARD =====
        (dashboard_router, None, ["dashboard"]),
    ]


# ================================
# MAIN REGISTER FUNCTION
# ================================
def register_routers(app: FastAPI):
    """
    Register all routers ke FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    registry = RouterRegistry()
    
    for router, prefix, tags in get_routers():
        registry.register(router, prefix, tags)
    
    registry.apply_to_app(app)
    
    log.info(f"✅ All routers registered successfully")


# ================================
# STATIC FILES
# ================================
def setup_static_files(app: FastAPI):
    """Setup static file serving"""
    static_path = settings.STATIC_DIR
    
    if not static_path.exists():
        log.warning(f"⚠️ Static directory not found: {static_path}")
        return
    
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    log.info(f"📦 Static files mounted from: {static_path}")