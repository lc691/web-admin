from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from app.templates import templates

from .repository import RequiredChannelRepository

router = APIRouter(prefix="/required-channels", tags=["Required Channels"])

repo = RequiredChannelRepository()


# =========================
# LIST (HTML)
# =========================
@router.get("/")
def list_required_channels(
    request: Request,
    bot_username: Optional[str] = Query(None),
    only_active: bool = Query(False),
):
    channels = repo.list_all(
        bot_username=bot_username,
        only_active=only_active,
    )

    return templates.TemplateResponse(
        "required_channels/list.html",
        {
            "request": request,
            "channels": channels,
            "bot_username": bot_username,
            "only_active": only_active,
        },
    )


# =========================
# CREATE (FORM SUBMIT)
# =========================
@router.post("/create")
def create_required_channel(
    username: str = Form(...),
    bot_username: str = Form(...),
    added_by: Optional[str] = Form(None),
):
    try:
        repo.create(
            username=username,
            bot_username=bot_username,
            added_by=added_by,
            is_active=True,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )


# =========================
# TOGGLE ACTIVE
# =========================
@router.post("/{channel_id}/toggle")
def toggle_required_channel(channel_id: int):
    data = repo.get_by_id(channel_id)
    if not data:
        raise HTTPException(status_code=404, detail="Channel not found")

    repo.update(
        channel_id,
        is_active=not data["is_active"],
    )

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )


# =========================
# EDIT PAGE (FORM)
# =========================
@router.get("/{channel_id}/edit")
def edit_required_channel_page(
    channel_id: int,
    request: Request,
):
    channel = repo.get_by_id(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return templates.TemplateResponse(
        "required_channels/edit.html",
        {
            "request": request,
            "channel": channel,
        },
    )


# =========================
# UPDATE (FORM SUBMIT)
# =========================
@router.post("/{channel_id}/edit")
def update_required_channel(
    channel_id: int,
    username: str = Form(...),
    is_active: bool = Form(False),
):
    channel = repo.get_by_id(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    repo.update(
        channel_id,
        username=username,
        is_active=is_active,
    )

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )

# =========================
# DELETE
# =========================
@router.post("/{channel_id}/delete")
def delete_required_channel(channel_id: int):
    deleted = repo.delete(channel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Channel not found")

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )
