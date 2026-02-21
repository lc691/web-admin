from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from itsdangerous import BadSignature

from app.core.auth import read_session

PUBLIC_PATHS = (
    "/login",
    "/logout",
)


def auth_middleware_factory():
    async def auth_middleware(request: Request, call_next):

        print("METHOD:", request.method)
        print("PATH:", request.url.path)
        print("COOKIES:", request.cookies)

        path = request.url.path

        if (
            path.startswith("/static")
            or path.startswith("/favicon")
            or path in PUBLIC_PATHS
        ):
            return await call_next(request)

        token = request.cookies.get("auth_session")  # pastikan pakai nama baru
        if not token:
            if request.method == "GET":
                return RedirectResponse("/login", status_code=303)
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
            )

        try:
            read_session(token)
        except BadSignature:
            if request.method == "GET":
                return RedirectResponse("/login", status_code=303)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid session"},
            )

        return await call_next(request)

    return auth_middleware
