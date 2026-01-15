from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.affiliate import crud_payout
from app.affiliate.crud_admin_audit_logs import log_admin_action
# from app.auth.dependencies import admin_required
from app.templates import templates

router = APIRouter(
    prefix="/affiliate/payouts",
    tags=["Affiliate Payout"],
)


# =========================
# LIST PAYOUT
# =========================
@router.get("", response_class=HTMLResponse)
# @admin_required
def payout_list(request: Request):
    batches = crud_payout.list_payout_batches()
    return templates.TemplateResponse(
        "affiliate/payout_list.html",
        {
            "request": request,
            "batches": batches,
            "title": "Affiliate Payout Batch",
        },
    )


# =========================
# PAYOUT DETAIL
# =========================
@router.get("/{batch_id}", response_class=HTMLResponse)
# @admin_required
def payout_detail(batch_id: int, request: Request):
    batch = crud_payout.get_payout_batch(batch_id)
    details = crud_payout.get_payout_details(batch_id)

    return templates.TemplateResponse(
        "affiliate/payout_detail.html",
        {
            "request": request,
            "batch": batch,
            "details": details,
        },
    )


# =========================
# MARK AS PAID
# =========================
@router.post("/{batch_id}/paid")
# @admin_required
def payout_mark_paid(batch_id: int, request: Request):
    admin_id = request.state.user_id

    crud_payout.mark_batch_paid(batch_id, admin_id)

    log_admin_action(
        admin_id=admin_id,
        action="affiliate_payout_paid",
        target_type="payout_batch",
        target_id=batch_id,
    )

    return RedirectResponse(url=f"/affiliate/payouts/{batch_id}", status_code=303)
