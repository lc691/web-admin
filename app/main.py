from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.base.routes import get_dashboard_stats

# Routers
from app.users.routes import router as user_router
from app.files.routes import router as files_router
from app.shows.routes import router as shows_router
from app.admins.routes import router as admins_router
from app.vip_users.routes import router as vip_user_router
from app.vip_logs.routes import router as vip_logs_router
from app.vip_packages.routes import router as vip_pakages_router
from app.vip_vouchers.routes import router as vip_voucheres_router


# Template Engine
from app.templates import templates

app = FastAPI()

# Include routers
app.include_router(admins_router)
app.include_router(user_router)
app.include_router(files_router)
app.include_router(shows_router)
app.include_router(vip_user_router)
app.include_router(vip_logs_router)
app.include_router(vip_pakages_router)
app.include_router(vip_voucheres_router)

# Static files (CSS, JS, Images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========================
# Route: Dashboard
# ========================
@app.get("/")
async def dashboard(request: Request):
    stats = get_dashboard_stats()
    return templates.TemplateResponse("base.html", {
        "request": request,
        "stats": stats
    })

# ========================
# Route: Login
# ========================
@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "path": request.url.path,
    })

# ========================
# (Optional) POST login
# ========================
@app.post("/login")
async def do_login(username: str = Form(...), password: str = Form(...)):
    # Proses login (dummy login)
    if username == "admin" and password == "123":
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/login", status_code=303)
