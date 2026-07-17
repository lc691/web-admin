from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.utils.logger import log


class BusinessError(Exception):
    """Exception untuk error bisnis."""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler untuk error validasi Pydantic."""
    log.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "errors": exc.errors()
        }
    )


async def business_exception_handler(request: Request, exc: BusinessError):
    """Handler untuk error bisnis."""
    log.warning(f"Business error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "details": exc.details
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler untuk error umum."""
    log.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    if request.app.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": str(exc),
                "type": exc.__class__.__name__
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )