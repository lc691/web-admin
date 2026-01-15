from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from psycopg2.extras import RealDictCursor
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from db.connect import get_dict_cursor

router = APIRouter()


# ---------------------------
# List all VIP packages
# ---------------------------
@router.get("/vip_packages", response_class=HTMLResponse)
async def list_vip_packages(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM vip_packages ORDER BY created_at DESC")
        packages = cursor.fetchall()

    return templates.TemplateResponse(
        "vip_packages/list.html",
        {"request": request, "packages": packages, "title": "Vip Packages"},
    )


# ---------------------------
# Create new VIP package (form page)
# ---------------------------
@router.get("/vip_packages/new")
def new_vip_package_form(request: Request):
    return templates.TemplateResponse(
        "vip_packages/form.html", {"request": request, "package": None}
    )


# ---------------------------
# Create new VIP package (submit)
# ---------------------------
@router.post("/vip_packages/new")
def create_vip_package(
    paket_name: str = Form(...),
    alias: str = Form(None),
    basic_days: int = Form(...),
    total_days: int = Form(...),
    is_promo_once: bool = Form(False),
    is_active: bool = Form(True),
    display_label: str = Form(None),
    price: int = Form(None),
    db=Depends(get_dict_cursor),
):
    with db as (cursor, conn):
        cursor.execute(
            """
            INSERT INTO vip_packages (paket_name, alias, basic_days, total_days, is_promo_once,
                is_active, display_label, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                paket_name,
                alias,
                basic_days,
                total_days,
                is_promo_once,
                is_active,
                display_label,
                price,
            ),
        )
        conn.commit()
    return RedirectResponse(url="/vip_packages", status_code=HTTP_302_FOUND)


# ---------------------------
# Edit VIP package (form page)
# ---------------------------
@router.get("/vip_packages/{paket_name}/edit", response_class=HTMLResponse)
def edit_package(paket_name: str, request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM vip_packages WHERE paket_name = %s", (paket_name,))
        package = cursor.fetchone()

    if not package:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan")

    return templates.TemplateResponse(
        "vip_packages/edit.html",
        {
            "request": request,
            "package": package,
        },
    )


# ---------------------------
# Edit VIP package (submit)
# ---------------------------
@router.post("/vip_packages/{paket_name}/edit")
def update_vip_package(
    paket_name: str,
    alias: Optional[str] = Form(None),
    basic_days: int = Form(...),
    total_days: int = Form(...),
    is_promo_once: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    display_label: Optional[str] = Form(None),
    price: Optional[int] = Form(None),
):
    is_promo_once_bool = is_promo_once is not None
    is_active_bool = is_active is not None

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE vip_packages
            SET alias=%s,
                basic_days=%s,
                total_days=%s,
                is_promo_once=%s,
                is_active=%s,
                display_label=%s,
                price=%s,
                updated_at=NOW()
            WHERE paket_name=%s
        """,
            (
                alias,
                basic_days,
                total_days,
                is_promo_once_bool,
                is_active_bool,
                display_label,
                price,
                paket_name,
            ),
        )
        conn.commit()

    return RedirectResponse("/vip_packages", status_code=HTTP_302_FOUND)


# ---------------------------
# Delete VIP package
# ---------------------------
@router.post("/vip_packages/{paket_name}/delete")
def delete_vip_package(paket_name: str, db=Depends(get_dict_cursor)):
    with db as (cursor, conn):
        cursor.execute("DELETE FROM vip_packages WHERE paket_name = %s", (paket_name,))
        conn.commit()
    return RedirectResponse(url="/vip_packages", status_code=HTTP_302_FOUND)
