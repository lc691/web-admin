"""
Channel Error Pages
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates import templates

router = APIRouter()


# =====================================================
# BAD REQUEST
# =====================================================

@router.get(
    "/channels/error/400",
    response_class=HTMLResponse,
)
async def bad_request(
    request: Request,
    message: str = "Bad Request",
):
    return templates.TemplateResponse(
        "errors/400.html",
        {
            "request": request,
            "message": message,
        },
        status_code=400,
    )


# =====================================================
# FORBIDDEN
# =====================================================

@router.get(
    "/channels/error/403",
    response_class=HTMLResponse,
)
async def forbidden(
    request: Request,
    message: str = "Access Denied",
):
    return templates.TemplateResponse(
        "errors/403.html",
        {
            "request": request,
            "message": message,
        },
        status_code=403,
    )


# =====================================================
# NOT FOUND
# =====================================================

@router.get(
    "/channels/error/404",
    response_class=HTMLResponse,
)
async def not_found(
    request: Request,
    message: str = "Channel not found",
):
    return templates.TemplateResponse(
        "errors/404.html",
        {
            "request": request,
            "message": message,
        },
        status_code=404,
    )


# =====================================================
# SERVER ERROR
# =====================================================

@router.get(
    "/channels/error/500",
    response_class=HTMLResponse,
)
async def server_error(
    request: Request,
    message: str = "Internal Server Error",
):
    return templates.TemplateResponse(
        "errors/500.html",
        {
            "request": request,
            "message": message,
        },
        status_code=500,
    )


__all__ = ["router"]