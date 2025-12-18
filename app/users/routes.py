from datetime import datetime

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

from app.templates import templates
from app.users import crud
from db.connect import get_dict_cursor

router = APIRouter(prefix="", tags=["Users"])

# ==========================================================
# FILTER MAP (SATU QUERY, BANYAK MODE)
# ==========================================================

FILTER_SQL = {
    "all": "is_active = TRUE",
    "vip": "is_vip = TRUE AND vip_expired > NOW()",
    "nonvip": "is_vip = FALSE OR vip_expired <= NOW()",
    "trial": "trial_given = TRUE AND (is_vip = FALSE OR vip_expired < CURRENT_DATE)",
    "abuse": "abuse_flag = TRUE",
    "affiliate": "referrer_user_id IS NOT NULL",
}

# ==========================================================
# LIST USERS (FAST + PAGINATION + SEARCH)
# ==========================================================


@router.get("/users", response_class=HTMLResponse)
def list_users(
    request: Request,
    q: str = "",
    filter: str = "all",
    page: int = 1,
    limit: int = 2000,
):
    if page < 1:
        page = 1

    offset = (page - 1) * limit
    where_clauses = []
    params = {
        "limit": limit,
        "offset": offset,
    }

    # filter utama
    where_clauses.append(FILTER_SQL.get(filter, "is_active = TRUE"))

    # search
    if q:
        where_clauses.append(
            """
            (
                username ILIKE %(q)s
                OR user_id::text ILIKE %(q)s
            )
            """
        )
        params["q"] = f"%{q}%"

    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT
            id,
            user_id,
            username,
            first_name,
            is_vip,
            vip_expired,
            is_active,
            created_at
        FROM users
        WHERE {where_sql}
        ORDER BY id DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(query, params)
        users = cursor.fetchall()

    return templates.TemplateResponse(
        "users/list.html",
        {
            "request": request,
            "users": users,
            "page": page,
            "filter": filter,
            "q": q,
            "limit": limit,
            "title": "Daftar Pengguna",
        },
    )


# ==========================================================
# ADD USER
# ==========================================================


@router.get("/users/add", response_class=HTMLResponse)
def add_user_form(request: Request):
    return templates.TemplateResponse(
        "users/add.html",
        {"request": request, "title": "Tambah User"},
    )


@router.post("/users/add")
def add_user(
    user_id: int = Form(...),
    username: str = Form(None),
    first_name: str = Form(None),
):
    crud.create_user(user_id, username, first_name)
    return RedirectResponse("/users", status_code=HTTP_303_SEE_OTHER)


# ==========================================================
# EDIT USER
# ==========================================================


@router.get("/users/{id}/edit", response_class=HTMLResponse)
def edit_user_form(id: int, request: Request):
    user = crud.get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    return templates.TemplateResponse(
        "users/edit.html",
        {"request": request, "user": user, "title": "Edit User"},
    )


@router.post("/users/{id}/edit")
def edit_user(
    id: int,
    username: str = Form(None),
    is_vip: str = Form("false"),
    vip_expired: str = Form(None),
    is_active: str = Form("true"),
):
    is_vip_bool = is_vip.lower() == "true"
    is_active_bool = is_active.lower() == "true"

    vip_expired_dt = None
    if vip_expired:
        try:
            vip_expired_dt = datetime.strptime(vip_expired, "%Y-%m-%dT%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Format tanggal salah")

    crud.update_user(
        id=id,
        username=username,
        is_vip=is_vip_bool,
        vip_expired=vip_expired_dt,
        is_active=is_active_bool,
    )

    return RedirectResponse("/users", status_code=HTTP_303_SEE_OTHER)


# ==========================================================
# DELETE USER
# ==========================================================


@router.post("/users/{id}/delete")
def delete_user(id: int):
    crud.delete_user(id)
    return RedirectResponse("/users", status_code=HTTP_303_SEE_OTHER)
