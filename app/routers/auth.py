from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.auth import (
    ADMIN_PASSWORD_HASH,
    ADMIN_USERNAME,
    create_session,
    verify_password,
)
from app.templates import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.post("/login")
async def do_login(
    username: str = Form(...),
    password: str = Form(...),
    remember: bool | None = Form(None),
):
    if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH):
        token = create_session({"user": username})
        resp = RedirectResponse("/", status_code=303)

        if remember:
            resp.set_cookie(
                "auth_session",  # ✅ GANTI
                token,
                httponly=True,
                samesite="lax",
                max_age=60 * 60 * 24 * 7,
            )
        else:
            resp.set_cookie(
                "auth_session",  # ✅ GANTI
                token,
                httponly=True,
                samesite="lax",
            )

        return resp

    return RedirectResponse("/login?error=1", status_code=303)


@router.get("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("auth_session")  # ✅ GANTI
    return resp
