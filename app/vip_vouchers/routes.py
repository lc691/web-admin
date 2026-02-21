from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from app.templates import templates
from db.connect import get_dict_cursor

router = APIRouter(prefix="/vip_vouchers", tags=["VIP Vouchers"])


# ============================
# List vouchers
# ============================
@router.get("", response_class=HTMLResponse)
def list_vouchers(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM vip_vouchers ORDER BY created_at DESC")
        vouchers = cursor.fetchall()

    return templates.TemplateResponse(
        "vip_vouchers/list.html",
        {"request": request, "vouchers": vouchers, "title": "VIP Vouchers"},
    )


# ============================
# Create voucher
# ============================
@router.get("/new", response_class=HTMLResponse)
def create_voucher_form(request: Request):
    return templates.TemplateResponse("vip_vouchers/new.html", {"request": request})


@router.post("/create")
def create_voucher(
    code: str = Form(...),
    duration_days: int = Form(...),
    expires_at: str = Form(None),
    created_by: str = Form(None),
    batch_uuid: str = Form(None),
):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            INSERT INTO vip_vouchers (code, duration_days, expires_at, created_by, batch_uuid)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (code, duration_days, expires_at, created_by, batch_uuid),
        )
        conn.commit()

    return RedirectResponse(url="/vip_vouchers", status_code=status.HTTP_303_SEE_OTHER)


# ============================
# Edit voucher
# ============================
@router.get("/{code}/edit", response_class=HTMLResponse)
def edit_voucher_form(code: str, request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM vip_vouchers WHERE code = %s", (code,))
        voucher = cursor.fetchone()

    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")

    return templates.TemplateResponse(
        "vip_vouchers/edit.html", {"request": request, "voucher": voucher}
    )


@router.post("/{code}/edit")
def edit_voucher(
    code: str,
    duration_days: int = Form(...),
    is_used: bool = Form(False),
    expires_at: str = Form(None),
    created_by: str = Form(None),
    batch_uuid: str = Form(None),
    used_by: int = Form(None),
):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE vip_vouchers
            SET duration_days = %s,
                is_used = %s,
                expires_at = %s,
                created_by = %s,
                batch_uuid = %s,
                used_by = %s
            WHERE code = %s
        """,
            (duration_days, is_used, expires_at, created_by, batch_uuid, used_by, code),
        )
        conn.commit()

    return RedirectResponse(url="/vip_vouchers", status_code=status.HTTP_303_SEE_OTHER)


# ============================
# Delete voucher
# ============================
@router.post("/{code}/delete")
def delete_voucher(code: str):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("DELETE FROM vip_vouchers WHERE code = %s", (code,))
        conn.commit()

    return RedirectResponse(url="/vip_vouchers", status_code=status.HTTP_303_SEE_OTHER)
