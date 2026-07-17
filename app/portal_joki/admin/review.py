"""
Portal Joki - Admin Review Routes

Routes untuk mengelola review portal joki.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse, RedirectResponse
from app.templates import templates

from app.dependencies.auth import require_admin
from app.portal_joki.services.review.approve import (
    PortalJokiApproveService,
)
from app.portal_joki.services.review.revisi import (
    PortalJokiRevisiService,
)
from app.portal_joki.services.review.comment import (
    PortalJokiCommentService,
)
from app.portal_joki.repositories.review.review_repo import (
    PortalJokiReviewRepository,
)
from app.portal_joki.repositories.penugasan.penugasan_repo import (
    PortalJokiPenugasanRepository,
)
from app.utils.logger import log

router = APIRouter(
    prefix="/admin/portal-joki/review",
    tags=["Portal Joki Admin"],
)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def get_review_status_label(status: int) -> str:
    """Get review status label."""
    status_map = {1: "Approved", 2: "Revisi", 3: "Rejected"}
    return status_map.get(status, "Unknown")

def get_review_status_color(status: int) -> str:
    """Get review status color."""
    color_map = {1: "success", 2: "warning", 3: "danger"}
    return color_map.get(status, "secondary")


# ==========================================================
# REVIEW LIST PAGE
# ==========================================================
@router.get(
    "/",
    name="portal_joki_admin_review",
)
async def review_list(
    request: Request,
    status: Optional[int] = Query(None, description="Filter by status"),
    penugasan_id: Optional[int] = Query(None, description="Filter by penugasan"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Admin review list page.
    """
    log.info(f"Admin review list: page={page}, status={status}, penugasan_id={penugasan_id}")

    try:
        admin = require_admin(request)

        offset = (page - 1) * limit

        # Get reviews
        if penugasan_id:
            data = PortalJokiReviewRepository.get_history(penugasan_id, limit)
            total = len(data)
        elif status is not None:
            data = PortalJokiReviewRepository.get_by_status(
                status=status,
                limit=limit,
                offset=offset,
            )
            total = PortalJokiReviewRepository.count(status=status)
        else:
            # Get all reviews - use get_all if available, or get by status with all statuses
            data = PortalJokiReviewRepository.get_by_status(
                status=1,  # Default to approved
                limit=limit,
                offset=offset,
            )
            total = PortalJokiReviewRepository.count()

        # Add status labels
        for item in data:
            item["status_label"] = get_review_status_label(item.get("status", 0))
            item["status_color"] = get_review_status_color(item.get("status", 0))

        # Calculate pagination
        total_pages = (total + limit - 1) // limit if total > 0 else 1

        return templates.TemplateResponse(
            "portal_joki/admin/review_list.html",
            {
                "request": request,
                "title": "Daftar Review",
                "admin": admin,
                "reviews": data,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "status": status,
                "penugasan_id": penugasan_id,
                "get_status_label": get_review_status_label,
                "get_status_color": get_review_status_color,
                "generated_at": datetime.now(),
            },
        )

    except Exception as e:
        log.error(f"Failed to load review list: {e}")
        return templates.TemplateResponse(
            "portal_joki/admin/review_list.html",
            {
                "request": request,
                "title": "Daftar Review",
                "error": str(e),
                "reviews": [],
                "total": 0,
                "page": 1,
                "limit": 20,
                "total_pages": 1,
                "generated_at": datetime.now(),
            },
        )


# ==========================================================
# REVIEW DETAIL PAGE
# ==========================================================
@router.get(
    "/{review_id}",
    name="portal_joki_admin_review_detail",
)
async def review_detail(
    request: Request,
    review_id: int,
):
    """
    Admin review detail page.
    """
    log.info(f"Admin review detail: ID={review_id}")

    try:
        admin = require_admin(request)

        review = PortalJokiReviewRepository.get(review_id)

        if not review:
            return templates.TemplateResponse(
                "portal_joki/admin/review_detail.html",
                {
                    "request": request,
                    "title": "Detail Review",
                    "error": "Review tidak ditemukan.",
                    "admin": admin,
                },
            )

        # Get penugasan detail
        penugasan = PortalJokiPenugasanRepository.get(review.get("penugasan_id"))

        review["status_label"] = get_review_status_label(review.get("status", 0))
        review["status_color"] = get_review_status_color(review.get("status", 0))

        return templates.TemplateResponse(
            "portal_joki/admin/review_detail.html",
            {
                "request": request,
                "title": "Detail Review",
                "admin": admin,
                "review": review,
                "penugasan": penugasan,
                "generated_at": datetime.now(),
            },
        )

    except Exception as e:
        log.error(f"Failed to load review detail: {e}")
        return templates.TemplateResponse(
            "portal_joki/admin/review_detail.html",
            {
                "request": request,
                "title": "Detail Review",
                "error": str(e),
                "admin": admin,
            },
        )


# ==========================================================
# APPROVE REVIEW (POST)
# ==========================================================
@router.post(
    "/{review_id}/approve",
    name="portal_joki_admin_review_approve",
)
async def review_approve(
    request: Request,
    review_id: int,
    komentar: Optional[str] = Form(None),
):
    """
    Approve review.
    """
    log.info(f"Approve review: ID={review_id}")

    try:
        admin = require_admin(request)

        # Get review to get penugasan_id
        review = PortalJokiReviewRepository.get(review_id)

        if not review:
            return JSONResponse({
                "success": False,
                "error": "Review tidak ditemukan.",
            }, status_code=404)

        penugasan_id = review.get("penugasan_id")

        if not penugasan_id:
            return JSONResponse({
                "success": False,
                "error": "Penugasan tidak ditemukan.",
            }, status_code=404)

        # Approve via service
        result = PortalJokiApproveService.execute(
            penugasan_id=penugasan_id,
            komentar=komentar or review.get("komentar"),
            reviewed_by=admin.get("username", "admin"),
            skip_upload_check=True,
        )

        if result.success:
            return JSONResponse({
                "success": True,
                "message": result.message,
                "review_id": result.review_id,
            })

        return JSONResponse({
            "success": False,
            "error": result.message,
        }, status_code=400)

    except Exception as e:
        log.error(f"Failed to approve review: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# REJECT REVIEW (POST)
# ==========================================================
@router.post(
    "/{review_id}/reject",
    name="portal_joki_admin_review_reject",
)
async def review_reject(
    request: Request,
    review_id: int,
    komentar: str = Form(...),
):
    """
    Reject review (send revision).
    """
    log.info(f"Reject review: ID={review_id}")

    try:
        admin = require_admin(request)

        if not komentar or not komentar.strip():
            return JSONResponse({
                "success": False,
                "error": "Komentar revisi wajib diisi.",
            }, status_code=400)

        # Get review to get penugasan_id
        review = PortalJokiReviewRepository.get(review_id)

        if not review:
            return JSONResponse({
                "success": False,
                "error": "Review tidak ditemukan.",
            }, status_code=404)

        penugasan_id = review.get("penugasan_id")

        if not penugasan_id:
            return JSONResponse({
                "success": False,
                "error": "Penugasan tidak ditemukan.",
            }, status_code=404)

        # Send revision via service
        result = PortalJokiRevisiService.execute(
            penugasan_id=penugasan_id,
            komentar=komentar,
            reviewed_by=admin.get("username", "admin"),
            skip_upload_check=True,
        )

        if result.success:
            return JSONResponse({
                "success": True,
                "message": result.message,
                "review_id": result.review_id,
            })

        return JSONResponse({
            "success": False,
            "error": result.message,
        }, status_code=400)

    except Exception as e:
        log.error(f"Failed to reject review: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# UPDATE COMMENT (POST)
# ==========================================================
@router.post(
    "/{review_id}/comment",
    name="portal_joki_admin_review_comment",
)
async def review_comment(
    request: Request,
    review_id: int,
    komentar: str = Form(...),
):
    """
    Update review comment.
    """
    log.info(f"Update review comment: ID={review_id}")

    try:
        admin = require_admin(request)

        if not komentar or not komentar.strip():
            return JSONResponse({
                "success": False,
                "error": "Komentar tidak boleh kosong.",
            }, status_code=400)

        result = PortalJokiCommentService.execute(
            review_id=review_id,
            komentar=komentar,
            updated_by=admin.get("username", "admin"),
        )

        if result.success:
            return JSONResponse({
                "success": True,
                "message": result.message,
                "data": result.data,
            })

        return JSONResponse({
            "success": False,
            "error": result.message,
        }, status_code=400)

    except Exception as e:
        log.error(f"Failed to update comment: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# GET REVIEW HISTORY (AJAX)
# ==========================================================
@router.get(
    "/history/{penugasan_id}",
    name="portal_joki_admin_review_history",
)
async def review_history(
    request: Request,
    penugasan_id: int,
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get review history for a penugasan (AJAX).
    """
    log.info(f"Get review history: penugasan_id={penugasan_id}")

    try:
        require_admin(request)

        data = PortalJokiReviewRepository.get_history(penugasan_id, limit)

        # Add status labels
        for item in data:
            item["status_label"] = get_review_status_label(item.get("status", 0))
            item["status_color"] = get_review_status_color(item.get("status", 0))

        return JSONResponse({
            "success": True,
            "data": data,
            "total": len(data),
            "penugasan_id": penugasan_id,
        })

    except Exception as e:
        log.error(f"Failed to get review history: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# GET REVIEW STATS (AJAX)
# ==========================================================
@router.get(
    "/stats",
    name="portal_joki_admin_review_stats",
)
async def review_stats(
    request: Request,
    penugasan_id: Optional[int] = Query(None),
):
    """
    Get review statistics (AJAX).
    """
    log.info(f"Get review stats: penugasan_id={penugasan_id}")

    try:
        require_admin(request)

        if penugasan_id:
            # Stats for specific penugasan
            counter = PortalJokiReviewRepository.get_counter(penugasan_id)
            return JSONResponse({
                "success": True,
                "data": counter,
                "penugasan_id": penugasan_id,
            })

        # Overall stats
        total = PortalJokiReviewRepository.count()
        approved = PortalJokiReviewRepository.count(status=1)
        revision = PortalJokiReviewRepository.count(status=2)
        rejected = PortalJokiReviewRepository.count(status=3)

        return JSONResponse({
            "success": True,
            "data": {
                "total": total,
                "approved": approved,
                "revision": revision,
                "rejected": rejected,
            },
        })

    except Exception as e:
        log.error(f"Failed to get review stats: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# PENDING REVIEWS (AJAX)
# ==========================================================
@router.get(
    "/pending",
    name="portal_joki_admin_review_pending",
)
async def review_pending(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get pending reviews (AJAX).
    """
    log.info(f"Get pending reviews: limit={limit}")

    try:
        require_admin(request)

        data = PortalJokiReviewRepository.get_pending_reviews(limit)

        for item in data:
            item["status_label"] = get_review_status_label(item.get("status", 0))
            item["status_color"] = get_review_status_color(item.get("status", 0))

        return JSONResponse({
            "success": True,
            "data": data,
            "total": len(data),
            "limit": limit,
        })

    except Exception as e:
        log.error(f"Failed to get pending reviews: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)