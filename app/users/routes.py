from datetime import datetime

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

from app.templates import templates
from app.users import crud
from db.connect import get_dict_cursor

router = APIRouter()

@router.get("/users", response_class=HTMLResponse)
def list_users(request: Request, search: str = "", vip_only: bool = False):
    where_clauses = []
    params = []

    if search:
        where_clauses.append("(username ILIKE %s OR CAST(user_id AS TEXT) ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    if vip_only:
        where_clauses.append("is_vip = TRUE")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
        SELECT * FROM users
        {where_sql}
        ORDER BY id ASC
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(query, tuple(params))
        users = cursor.fetchall()

    return templates.TemplateResponse("users/list.html", {
        "request": request,
        "users": users,
        "title": "Daftar Semua Pengguna"
    })


@router.get("/users/vip", response_class=HTMLResponse)
def get_vip_users(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT * FROM users
            WHERE is_vip = TRUE AND vip_expired > NOW()
            ORDER BY vip_expired DESC
        """)
        users = cursor.fetchall()

    return templates.TemplateResponse("users/list.html", {
        "request": request,
        "users": users,
        "title": "Daftar Pengguna VIP"
    })

@router.get("/users/nonvip", response_class=HTMLResponse)
def get_nonvip_users(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT * FROM users
            WHERE is_vip = FALSE OR vip_expired <= NOW()
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()

    return templates.TemplateResponse("users/list.html", {
        "request": request,
        "users": users,
        "title": "Daftar Pengguna Non-VIP"
    })

@router.get("/users/trial", response_class=HTMLResponse)
def get_trial_users(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT * FROM users
            WHERE trial_given = TRUE AND (is_vip = FALSE OR vip_expired < CURRENT_DATE)
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()

    return templates.TemplateResponse("users/list.html", {
        "request": request,
        "users": users,
        "title": "Daftar Pengguna Trial"
    })

@router.get("/users/referred", response_class=HTMLResponse)
def get_referred_users(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT * FROM users
            WHERE referred_by IS NOT NULL
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()

    return templates.TemplateResponse("users/list.html", {
        "request": request,
        "users": users,
        "title": "Daftar Pengguna dari Referral"
    })


@router.get("/users/add", response_class=HTMLResponse)
def add_user_form(request: Request):
    return templates.TemplateResponse("users/add.html", {"request": request})

@router.get("/users/delete/{id}")
def delete_user(id: int):
    crud.delete_user(id)
    return RedirectResponse("/users", status_code=302)

@router.get("/users/{id}/edit", response_class=HTMLResponse)
def edit_user_form(id: int, request: Request):
    user = crud.get_user_by_id(id)  # Pastikan hasilnya Dict / NamedTuple
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("users/edit.html", {"request": request, "user": user})

@router.post("/users/{user_id}/delete")
def delete_user(user_id: int, request: Request):
    crud.delete_user(user_id)
    return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)

@router.post("/users/add")
def add_user(user_id: int = Form(...), username: str = Form(...), first_name: str = Form(...)):
    crud.create_user(user_id, username, first_name)
    return RedirectResponse("/users", status_code=302)

@router.post("/users/edit/{id}")
def edit_user(
    id: int,
    username: str = Form(...),
    is_vip: str = Form("false"),  # HTML form always sends string, even for bools
    vip_expired: str = Form(None),
):
    is_vip_bool = is_vip.lower() == "true"

    # Parse datetime-local (format: 'YYYY-MM-DDTHH:MM')
    vip_expired_dt = None
    if vip_expired:
        try:
            vip_expired_dt = datetime.strptime(vip_expired, "%Y-%m-%dT%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Format tanggal tidak valid")

    crud.update_user(id, username, is_vip_bool, vip_expired_dt)
    return RedirectResponse("/users", status_code=302)