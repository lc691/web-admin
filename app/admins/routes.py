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
    return templates.TemplateResponse("admins/list.html", {
        "request": request,
        "admins": admins,
        "title": "Daftar Admin"
    })


# Form Tambah Admin
@router.get("/admins/add", response_class=HTMLResponse)
async def add_admin_form(request: Request):
    return templates.TemplateResponse("admins/add.html", {
        "request": request,
        "title": "Tambah Admin Baru"
    })

# Submit Tambah Admin
@router.post("/admins/add")
async def add_admin_submit(
    user_id: int = Form(...),
    first_name: str = Form(...),
    username: str = Form(...)
):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("INSERT INTO admins (user_id, first_name, username) VALUES (%s, %s, %s)", (user_id, first_name, username))
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
    return templates.TemplateResponse("admins/edit.html", {
        "request": request,
        "admin": admin,
        "title": "Edit Admin"
    })

# Submit Edit
@router.post("/admins/edit/{user_id}")
async def edit_admin_submit(user_id: int, first_name: str = Form(...), username: str = Form(...)):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("""
            UPDATE admins
            SET first_name = %s, username = %s
            WHERE user_id = %s
        """, (first_name, username, user_id))
        conn.commit()
    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)

# Hapus Admin
@router.post("/admins/delete/{user_id}")
async def delete_admin(user_id: int):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("DELETE FROM admins WHERE user_id = %s", (user_id,))
        conn.commit()
    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)