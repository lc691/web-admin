"""
SoundON Admin Dashboard - Aplikasi Utama
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.middleware import setup_middleware
from app.core.routes import register_routers
from app.core.exceptions import (
    validation_exception_handler,
    business_exception_handler,
    general_exception_handler,
    BusinessError,
)
from app.utils.logger import log


# ================================
# Siklus Hidup (Startup / Shutdown)
# ================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Menangani event saat aplikasi mulai dan berhenti."""
    log.info(f"🚀 Menjalankan {settings.APP_NAME} v{settings.APP_VERSION}")
    log.info(f"Mode debug: {settings.DEBUG}")
    log.info(f"Environment: {settings.ENVIRONMENT}")
    log.info(f"Cookie autentikasi: {settings.AUTH_COOKIE_NAME}")
    
    # Test database connection
    try:
        from app.core.database import test_connection
        if test_connection():
            log.info("✅ Database connected successfully")
        else:
            log.warning("⚠️ Database connection failed")
    except ImportError:
        log.warning("⚠️ Database module not found")
    except Exception as e:
        log.error(f"❌ Database error: {e}")
    
    yield
    
    log.info(f"🛑 Mematikan {settings.APP_NAME}")


# ================================
# Pengaturan File Statis
# ================================
def setup_static_files(app: FastAPI):
    """Memasang direktori file statis."""
    static_dir = settings.STATIC_DIR

    if not static_dir.exists():
        log.warning(f"⚠️ Direktori statis tidak ditemukan: {static_dir}")
        return

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    log.info(f"📦 File statis dipasang di: {static_dir}")


# ================================
# Pabrik Aplikasi
# ================================
def create_app() -> FastAPI:
    """Membuat dan mengkonfigurasi aplikasi FastAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )

    # Register exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(BusinessError, business_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Setup middleware, routes, dan static files
    setup_middleware(app)
    register_routers(app)
    setup_static_files(app)

    return app


# ================================
# Instance Aplikasi
# ================================
app = create_app()


# ================================
# Menjalankan (Hanya untuk Pengembangan)
# ================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )