from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from db.connect import get_dict_cursor, get_dict_cursor_dep

from .services.trusted_ip import invalidate_trusted_ip_cache

router = APIRouter()


# ---------------------------
# List all trusted IPs
# ---------------------------
@router.get("/trusted_ips", response_class=HTMLResponse)
async def list_trusted_ips(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM trusted_ips ORDER BY created_at DESC")
        items = cursor.fetchall()

    return templates.TemplateResponse(
        "trusted_ips/list.html",
        {
            "request": request,
            "items": items,
            "title": "Trusted IPs",
        },
    )


# ---------------------------
# Create trusted IP (form)
# ---------------------------
@router.get("/trusted_ips/new", response_class=HTMLResponse)
def new_trusted_ip_form(request: Request):
    return templates.TemplateResponse(
        "trusted_ips/form.html",
        {
            "request": request,
            "item": None,
        },
    )


# ---------------------------
# Create trusted IP (submit)
# ---------------------------
@router.post("/trusted_ips/new")
def create_trusted_ip(
    ip: str = Form(...),
    description: str | None = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    cursor.execute(
        """
        INSERT INTO trusted_ips (ip, description)
        VALUES (%s, %s)
        ON CONFLICT (ip) DO UPDATE
        SET description = EXCLUDED.description
        """,
        (ip, description),
    )
    conn.commit()

    # 🔥 invalidate cache supaya webhook langsung aware
    invalidate_trusted_ip_cache()

    return RedirectResponse(
        url="/trusted_ips",
        status_code=HTTP_302_FOUND,
    )


# ---------------------------
# Edit trusted IP (form)
# ---------------------------
@router.get("/trusted_ips/{ip}/edit", response_class=HTMLResponse)
def edit_trusted_ip(ip: str, request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            "SELECT * FROM trusted_ips WHERE ip = %s",
            (ip,),
        )
        item = cursor.fetchone()

    if not item:
        raise HTTPException(status_code=404, detail="IP tidak ditemukan")

    return templates.TemplateResponse(
        "trusted_ips/edit.html",
        {
            "request": request,
            "item": item,
        },
    )


# ---------------------------
# Edit trusted IP (submit)
# ---------------------------
@router.post("/trusted_ips/{ip}/edit")
def update_trusted_ip(
    ip: str,
    description: str | None = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    cursor.execute(
        """
        UPDATE trusted_ips
        SET description = %s
        WHERE ip = %s
        """,
        (description, ip),
    )
    conn.commit()

    invalidate_trusted_ip_cache()

    return RedirectResponse(
        url="/trusted_ips",
        status_code=HTTP_302_FOUND,
    )


# ---------------------------
# Delete trusted IP
# ---------------------------
@router.post("/trusted_ips/{ip}/delete")
def delete_trusted_ip(
    ip: str,
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    cursor.execute(
        "DELETE FROM trusted_ips WHERE ip = %s",
        (ip,),
    )
    conn.commit()

    invalidate_trusted_ip_cache()

    return RedirectResponse(
        url="/trusted_ips",
        status_code=HTTP_302_FOUND,
    )
