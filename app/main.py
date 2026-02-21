from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.admins.routes import router as admins_router
from app.affiliate.router_payout import router as affiliate_router_payout
from app.affiliate.routes import router as affiliate_router
from app.base.routes import get_dashboard_stats
from app.channel.routes import router as channel_router
from app.core.middleware import auth_middleware_factory
from app.donation_logs.routes import router as donation_logs_router
from app.platform.routes import router as platform_router
from app.referrals.routes import router as referral_router

# from app.files.routes import router as files_router
from app.routers.auth import router as auth_router
from app.routers.files import router as files_router
from app.routers.show_files import router as shows_files_router
from app.shows.routes import router as shows_router

# Template Engine
from app.templates import templates
from app.trust_ip.routes import router as trust_ip_router

# Routers
from app.users.routes import router as user_router
from app.vip_logs.routes import router as vip_logs_router
from app.vip_packages.routes import router as vip_pakages_router
from app.vip_users.routes import router as vip_user_router
from app.vip_vouchers.routes import router as vip_voucheres_router

app = FastAPI()

# 1️⃣ Session middleware dulu
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key",
)

# 2️⃣ Baru auth middleware
app.middleware("http")(auth_middleware_factory())

# Include routers
app.include_router(auth_router)
app.include_router(admins_router)
app.include_router(user_router)
app.include_router(files_router)
app.include_router(shows_files_router)
app.include_router(shows_router)
app.include_router(vip_user_router)
app.include_router(vip_logs_router)
app.include_router(donation_logs_router)
app.include_router(vip_pakages_router)
app.include_router(vip_voucheres_router)
app.include_router(referral_router)
app.include_router(affiliate_router)
app.include_router(affiliate_router_payout)
app.include_router(channel_router)
app.include_router(trust_ip_router)
app.include_router(platform_router)

BASE_DIR = Path(__file__).resolve().parent.parent  # project_root
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# ========================
# Route: Dashboard
# ========================
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = get_dashboard_stats()
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "stats": stats},
    )
