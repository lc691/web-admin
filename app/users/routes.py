from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates

from .service import delete_user, get_user, list_users, update_user

router = APIRouter()


@router.get("/users", response_class=HTMLResponse)
def list_users_view(
    request: Request,
    filter: str | None = None,  # vip | nonvip | trial | affiliate
):
    users = list_users(filter=filter)

    return templates.TemplateResponse(
        "users/list.html",
        {
            "request": request,
            "users": users,
            "filter": filter,
        },
    )


@router.get("/users/edit/{user_id}", response_class=HTMLResponse)
def edit_user_form(request: Request, user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(404, "User tidak ditemukan")

    return templates.TemplateResponse(
        "users/edit.html",
        {"request": request, "user": user},
    )


@router.post("/users/edit/{user_id}")
def update_user_post(
    user_id: int,
    username: str = Form(""),
    is_vip: bool = Form(False),
    is_active: bool = Form(True),
):
    update_user(
        id=user_id,
        username=username or None,
        is_vip=is_vip,
        vip_expired=None,
        is_active=is_active,
    )
    return RedirectResponse("/users", status_code=303)


@router.post("/users/delete/{user_id}")
def delete_user_post(user_id: int):
    delete_user(user_id)
    return RedirectResponse("/users", status_code=303)
