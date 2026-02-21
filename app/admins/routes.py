from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from db.connect import get_dict_cursor

router = APIRouter()


@router.get("/admins", response_class=HTMLResponse)
async def list_admins(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM admins ORDER BY user_id DESC")
        admins = cursor.fetchall()
    return templates.TemplateResponse(
        "admins/list.html",
        {"request": request, "admins": admins, "title": "Daftar Admin"},
    )


# Form Tambah Admin
@router.get("/admins/add", response_class=HTMLResponse)
async def add_admin_form(request: Request):
    return templates.TemplateResponse(
        "admins/add.html", {"request": request, "title": "Tambah Admin Baru"}
    )


# Submit Tambah Admin
@router.post("/admins/add")
async def add_admin_submit(
    user_id: int = Form(...), first_name: str = Form(...), username: str = Form(...)
):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            "INSERT INTO admins (user_id, first_name, username) VALUES (%s, %s, %s)",
            (user_id, first_name, username),
        )
        conn.commit()
    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)


# Form Edit
@router.get("/admins/edit/{user_id}", response_class=HTMLResponse)
async def edit_admin_form(request: Request, user_id: int):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM admins WHERE user_id = %s", (user_id,))
        admin = cursor.fetchone()
    if not admin:
        return HTMLResponse("Admin tidak ditemukan", status_code=404)
    return templates.TemplateResponse(
        "admins/edit.html", {"request": request, "admin": admin, "title": "Edit Admin"}
    )


# Submit Edit
@router.post("/admins/edit/{user_id}")
async def edit_admin_submit(
    user_id: int, first_name: str = Form(...), username: str = Form(...)
):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE admins
            SET first_name = %s, username = %s
            WHERE user_id = %s
        """,
            (first_name, username, user_id),
        )
        conn.commit()
    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)


# Hapus Admin
@router.post("/admins/delete/{user_id}")
async def delete_admin(user_id: int):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("DELETE FROM admins WHERE user_id = %s", (user_id,))
        conn.commit()
    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)


@router.get("/admins/retention", response_class=HTMLResponse)
async def retention_dashboard(request: Request):

    with get_dict_cursor() as (cursor, _):

        # Total reminder
        cursor.execute("""
            SELECT COUNT(*)
            FROM retention_log
            WHERE stage = 'strong_10d';
        """)
        total = cursor.fetchone()["count"]

        # Total converted
        cursor.execute("""
            SELECT COUNT(*)
            FROM retention_log
            WHERE stage = 'strong_10d'
            AND converted = TRUE;
        """)
        converted = cursor.fetchone()["count"]

        # 14 hari terakhir
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE converted = TRUE) AS converted
            FROM retention_log
            WHERE stage = 'strong_10d'
            AND sent_at >= NOW() - INTERVAL '14 days';
        """)
        last_14 = cursor.fetchone()

        # Adaptive distribution
        cursor.execute("""
            SELECT offset_days, COUNT(*) AS users
            FROM retention_adaptive
            GROUP BY offset_days
            ORDER BY offset_days;
        """)
        adaptive = cursor.fetchall()

    rate_all = (converted / total * 100) if total else 0
    rate_14 = (last_14["converted"] / last_14["total"] * 100) if last_14["total"] else 0

    return templates.TemplateResponse(
        "admins/retention_dashboard.html",
        {
            "request": request,
            "path": request.url.path,
            "title": "Retention Dashboard",
            "total": total,
            "converted": converted,
            "rate_all": round(rate_all, 2),
            "rate_14": round(rate_14, 2),
            "adaptive": adaptive,
        },
    )
