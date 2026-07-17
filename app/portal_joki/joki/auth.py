from functools import wraps
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.portal_joki.services.auth.login import (
    PortalJokiLoginService,
)



router = APIRouter(
    prefix="/portal-joki",
    tags=["Portal Joki Auth"],
)

templates = Jinja2Templates(
    directory="app/portal_joki/templates"
)


# ==========================================================
# LOGIN PAGE
# ==========================================================

@router.get(
    "/login",
    name="portal_joki_login",
)
async def login_page(
    request: Request,
):

    if request.session.get("portal_joki"):

        return RedirectResponse(
            "/portal-joki/dashboard",
            status_code=302,
        )

    return templates.TemplateResponse(
        "portal_joki/login.html",
        {
            "request": request,
            "title": "Login Joki",
        },
    )


# ==========================================================
# LOGIN PROCESS
# ==========================================================

@router.post(
    "/login",
    name="portal_joki_login_post",
)
async def login_process(
    request: Request,

    kode: str = Form(...),

    password: str = Form(...),
):

    result = PortalJokiLoginService.execute(
        kode=kode,
        password=password,
    )

    if not result.success:

        return templates.TemplateResponse(
            "portal_joki/login.html",
            {
                "request": request,
                "title": "Login Joki",
                "error": result.message,
                "kode": kode,
            },
            status_code=400,
        )

    request.session["portal_joki"] = {
        "id": result.user["id"],
        "nama": result.user["nama"],
        "kode": result.user["kode"],
    }

    return RedirectResponse(
        "/portal-joki/dashboard",
        status_code=302,
    )


# ==========================================================
# LOGOUT
# ==========================================================

@router.get(
    "/logout",
    name="portal_joki_logout",
)
async def logout(
    request: Request,
):

    request.session.pop(
        "portal_joki",
        None,
    )

    return RedirectResponse(
        "/portal-joki/login",
        status_code=302,
    )


# ==========================================================
# SESSION
# ==========================================================

def get_current_joki(
    request: Request,
):

    return request.session.get(
        "portal_joki"
    )