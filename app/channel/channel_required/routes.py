import logging
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from app.templates import templates

from .repository import RequiredChannelRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/required-channels", tags=["Required Channels"])
repo = RequiredChannelRepository()


# ==========================================================
# VALIDATION HELPERS
# ==========================================================

def validate_username(username: str) -> str:
    """Validate and clean username."""
    username = username.strip()
    if not username:
        raise HTTPException(400, "Username wajib diisi")
    if len(username) < 2:
        raise HTTPException(400, "Username minimal 2 karakter")
    if not username.startswith('@'):
        username = f"@{username}"
    return username


def validate_bot_username(bot_username: str) -> str:
    """Validate and clean bot username."""
    bot_username = bot_username.strip()
    if not bot_username:
        raise HTTPException(400, "Bot username wajib diisi")
    if not bot_username.startswith('@'):
        bot_username = f"@{bot_username}"
    return bot_username


# ==========================================================
# LIST (HTML)
# ==========================================================
@router.get("/")
def list_required_channels(
    request: Request,
    bot_username: Optional[str] = Query(None, description="Filter by bot username"),
    only_active: bool = Query(False, description="Only show active channels"),
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


# ==========================================================
# LIST (JSON API)
# ==========================================================
@router.get("/api")
def list_required_channels_api(
    bot_username: Optional[str] = Query(None),
    only_active: bool = Query(False),
):
    channels = repo.list_all(
        bot_username=bot_username,
        only_active=only_active,
    )
    return {
        "success": True,
        "data": channels,
        "total": len(channels),
        "filters": {
            "bot_username": bot_username,
            "only_active": only_active,
        },
    }


# ==========================================================
# CREATE (FORM SUBMIT)
# ==========================================================
@router.post("/create")
def create_required_channel(
    request: Request,
    username: str = Form(...),
    bot_username: str = Form(...),
    added_by: Optional[str] = Form(None),
):
    # Validasi
    username = validate_username(username)
    bot_username = validate_bot_username(bot_username)
    
    # Cek duplikat
    existing = repo.get_by_username(username, bot_username)
    if existing:
        raise HTTPException(
            400, 
            f"Channel {username} sudah terdaftar untuk bot {bot_username}"
        )
    
    try:
        logger.info(f"Creating required channel: {username} for bot {bot_username}")
        repo.create(
            username=username,
            bot_username=bot_username,
            added_by=added_by,
            is_active=True,
        )
        logger.info(f"Required channel created successfully: {username}")
    except Exception as e:
        logger.error(f"Failed to create required channel: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )


# ==========================================================
# TOGGLE ACTIVE
# ==========================================================
@router.post("/{channel_id}/toggle")
def toggle_required_channel(channel_id: int):
    channel = repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    new_status = not channel["is_active"]
    logger.info(f"Toggling channel {channel_id} to {new_status}")
    
    repo.update(
        channel_id,
        is_active=new_status,
    )

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )


# ==========================================================
# EDIT PAGE (FORM)
# ==========================================================
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


# ==========================================================
# UPDATE (FORM SUBMIT)
# ==========================================================
@router.post("/{channel_id}/edit")
def update_required_channel(
    channel_id: int,
    username: str = Form(...),
    is_active: bool = Form(False),
):
    channel = repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Validasi username
    username = validate_username(username)
    
    # Cek duplikat (kecuali dirinya sendiri)
    existing = repo.get_by_username(username)
    if existing and existing["id"] != channel_id:
        raise HTTPException(
            400, 
            f"Username {username} sudah digunakan oleh channel lain"
        )

    logger.info(f"Updating channel {channel_id}: {username}")
    repo.update(
        channel_id,
        username=username,
        is_active=is_active,
    )

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )


# ==========================================================
# DELETE
# ==========================================================
@router.post("/{channel_id}/delete")
def delete_required_channel(channel_id: int):
    channel = repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    logger.info(f"Deleting required channel {channel_id}: {channel.get('username')}")
    deleted = repo.delete(channel_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Channel not found")

    return RedirectResponse(
        url="/required-channels/",
        status_code=303,
    )


# ==========================================================
# BULK CREATE (JSON)
# ==========================================================
@router.post("/bulk-create")
def bulk_create_required_channels(
    request: Request,
):
    import json
    
    try:
        body = request.body()
        data = json.loads(body)
        
        if not isinstance(data, list):
            raise HTTPException(400, "Data harus berupa array")
        
        if len(data) > 100:
            raise HTTPException(400, "Maksimal 100 channel per request")
        
        results = repo.bulk_create(data)
        
        return {
            "success": True,
            "created": len(results),
            "data": results,
        }
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON format")
    except Exception as e:
        logger.error(f"Bulk create failed: {str(e)}")
        raise HTTPException(400, str(e))


# ==========================================================
# STATS
# ==========================================================
@router.get("/stats")
def get_required_channels_stats(
    bot_username: Optional[str] = Query(None),
):
    total = len(repo.list_all())
    active = repo.get_active_count(bot_username)
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "bot_username": bot_username,
    }