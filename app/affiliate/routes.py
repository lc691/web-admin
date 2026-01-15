from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.affiliate import (crud, crud_abuse_logs, crud_admin_actions,
                           crud_admin_audit_logs, crud_commission_logs,
                           crud_withdraw_requests)
from app.templates import templates

router = APIRouter(
    prefix="/affiliate",
    tags=["Affiliate"],
)


# ============================================================
# HELPER: Render List Template
# ============================================================
def render_affiliate_list(request: Request, transactions: list, title: str, **context):
    if not transactions:
        raise HTTPException(status_code=404, detail="Data transaksi tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/list.html",
        {
            "request": request,
            "transactions": transactions,
            "title": title,
            **context,
        },
    )


# ============================================================
# 📋 Semua Transaksi Affiliate
# ============================================================
@router.get("/transactions", response_class=HTMLResponse)
def list_affiliate_transactions(
    request: Request,
    page: int = 1,
    limit: int = 20,
):
    data = crud.get_all_transactions(page, limit)
    return templates.TemplateResponse(
        "affiliate/list.html",
        {
            "request": request,
            "transactions": data["items"],
            "page": data["page"],
            "limit": data["limit"],
            "total": data["total"],
            "title": "Affiliate Transactions",
        },
    )


# ============================================================
# 👤 Transaksi oleh Referrer
# ============================================================
@router.get("/transactions/referrer/{referrer_user_id}", response_class=HTMLResponse)
def transactions_by_referrer(
    referrer_user_id: int,
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    transactions = crud.get_transactions_by_referrer(
        referrer_user_id,
        limit=limit,
        offset=offset,
    )

    return render_affiliate_list(
        request=request,
        transactions=transactions,
        title=f"Transaksi Affiliate — Referrer {referrer_user_id}",
        referrer_user_id=referrer_user_id,
    )


# ============================================================
# 👥 Transaksi oleh Referred User
# ============================================================
@router.get("/transactions/referred/{referred_user_id}", response_class=HTMLResponse)
def transactions_by_referred_user(
    referred_user_id: int,
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    transactions = crud.get_transactions_by_referred_user(
        referred_user_id,
        limit=limit,
        offset=offset,
    )

    return render_affiliate_list(
        request=request,
        transactions=transactions,
        title=f"Transaksi Affiliate — User {referred_user_id}",
        referred_user_id=referred_user_id,
    )


# ============================================================
# 💎 Transaksi berdasarkan Paket VIP
# ============================================================
@router.get("/transactions/package/{package_name}", response_class=HTMLResponse)
def transactions_by_package(
    package_name: str,
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    transactions = crud.get_transactions_by_package(
        package_name=package_name,
        limit=limit,
        offset=offset,
    )

    return render_affiliate_list(
        request=request,
        transactions=transactions,
        title=f"Transaksi Affiliate — Paket {package_name}",
        vip_package_name=package_name,
    )


from app.affiliate import crud_leaderboard


# =========================
# 🏆 Affiliate Leaderboard
# =========================
@router.get("/leaderboard", response_class=HTMLResponse)
def affiliate_leaderboard(request: Request):

    leaderboard = crud_leaderboard.get_affiliate_leaderboard(limit=20)

    return templates.TemplateResponse(
        "affiliate/leaderboard.html",
        {
            "request": request,
            "leaderboard": leaderboard,
            "title": "Affiliate Leaderboard",
            "active_menu": "affiliate_leaderboard",
        },
    )


# =========================
# 📋 Semua Log Komisi Affiliate
# =========================
@router.get("/commission-logs", response_class=HTMLResponse)
def list_commission_logs(request: Request):
    logs = crud_commission_logs.get_all_commission_logs()
    return templates.TemplateResponse(
        "affiliate/commission-logs.html",
        {
            "request": request,
            "logs": logs,
            "title": "Affiliate Commission Logs",
        },
    )


# =========================
# 👤 Log Komisi by Referrer
# =========================
@router.get("/commission-logs/referrer/{user_id}", response_class=HTMLResponse)
def commission_logs_by_referrer(user_id: int, request: Request):
    logs = crud_commission_logs.get_commission_logs_by_referrer(user_id)

    if not logs:
        raise HTTPException(404, "Log komisi untuk referrer ini tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/commission-logs.html",
        {
            "request": request,
            "logs": logs,
            "referrer_user_id": user_id,
            "title": f"Komisi Affiliate - Referrer {user_id}",
        },
    )


# =========================
# 👥 Log Komisi by Referred User
# =========================
@router.get("/commission-logs/referred/{user_id}", response_class=HTMLResponse)
def commission_logs_by_referred(user_id: int, request: Request):
    logs = crud_commission_logs.get_commission_logs_by_referred(user_id)

    if not logs:
        raise HTTPException(404, "Log komisi untuk user ini tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/commission-logs.html",
        {
            "request": request,
            "logs": logs,
            "referred_user_id": user_id,
            "title": f"Komisi Affiliate - User {user_id}",
        },
    )


# =========================
# 📋 Semua Abuse Logs
# =========================
@router.get("/abuse-logs", response_class=HTMLResponse)
def list_abuse_logs(request: Request):
    logs = crud_abuse_logs.get_all_abuse_logs()
    return templates.TemplateResponse(
        "affiliate/abuse_logs.html",
        {
            "request": request,
            "logs": logs,
            "title": "Affiliate Abuse Logs",
        },
    )


# =========================
# 👤 Abuse Logs by User
# =========================
@router.get("/abuse-logs/user/{user_id}", response_class=HTMLResponse)
def abuse_logs_by_user(user_id: int, request: Request):
    logs = crud_abuse_logs.get_abuse_logs_by_user(user_id)

    if not logs:
        raise HTTPException(404, "Abuse log tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/abuse_logs.html",
        {
            "request": request,
            "logs": logs,
            "user_id": user_id,
            "title": f"Abuse Logs - User {user_id}",
        },
    )


# =========================
# 👤 Abuse Logs by Referrer
# =========================
@router.get("/abuse-logs/referrer/{user_id}", response_class=HTMLResponse)
def abuse_logs_by_referrer(user_id: int, request: Request):
    logs = crud_abuse_logs.get_abuse_logs_by_referrer(user_id)

    if not logs:
        raise HTTPException(404, "Abuse log tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/abuse_logs.html",
        {
            "request": request,
            "logs": logs,
            "referrer_user_id": user_id,
            "title": f"Abuse Logs - Referrer {user_id}",
        },
    )


# =========================
# 📋 Semua Admin Actions
# =========================
@router.get("/admin-actions", response_class=HTMLResponse)
def list_admin_actions(request: Request):
    actions = crud_admin_actions.get_all_admin_actions()
    return templates.TemplateResponse(
        "affiliate/admin_actions.html",
        {
            "request": request,
            "actions": actions,
            "title": "Affiliate Admin Actions",
        },
    )


# =========================
# 👤 Actions by Admin
# =========================
@router.get("/admin-actions/admin/{admin_id}", response_class=HTMLResponse)
def admin_actions_by_admin(admin_id: int, request: Request):
    actions = crud_admin_actions.get_actions_by_admin(admin_id)

    if not actions:
        raise HTTPException(404, "Admin action tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/admin_actions.html",
        {
            "request": request,
            "actions": actions,
            "admin_id": admin_id,
            "title": f"Admin Actions - Admin {admin_id}",
        },
    )


# =========================
# 🎯 Actions by Target
# =========================
@router.get(
    "/admin-actions/target/{target_type}/{target_id}",
    response_class=HTMLResponse,
)
def admin_actions_by_target(
    target_type: str,
    target_id: int,
    request: Request,
):
    actions = crud_admin_actions.get_actions_by_target(target_type, target_id)

    if not actions:
        raise HTTPException(404, "Admin action tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/admin_actions.html",
        {
            "request": request,
            "actions": actions,
            "target_type": target_type,
            "target_id": target_id,
            "title": f"Admin Actions - {target_type} {target_id}",
        },
    )


# =========================
# 📋 Semua Withdraw
# =========================
@router.get("/withdraw-requests", response_class=HTMLResponse)
def list_withdraw_requests(request: Request, status: str | None = None):
    requests_ = (
        crud_withdraw_requests.get_withdraws_by_status(status)
        if status
        else crud_withdraw_requests.get_withdraws_by_status("pending")
    )

    return templates.TemplateResponse(
        "affiliate/withdraw_requests.html",
        {
            "request": request,
            "requests": requests_,
            "title": "Affiliate Withdraw Requests",
        },
    )


# =========================
# ⏳ Withdraw Pending
# =========================
@router.get("/withdraw-requests/pending", response_class=HTMLResponse)
def pending_withdraw_requests(request: Request):
    requests_ = crud_withdraw_requests.get_withdraws_by_status("pending")

    return templates.TemplateResponse(
        "affiliate/withdraw_requests.html",
        {
            "request": request,
            "requests": requests_,
            "title": "Pending Withdraw Requests",
        },
    )


# =========================
# 👤 Withdraw by User
# =========================
@router.get("/withdraw-requests/user/{user_id}", response_class=HTMLResponse)
def withdraw_requests_by_user(user_id: int, request: Request):
    requests_ = crud_withdraw_requests.get_withdraw_history(user_id)

    if not requests_:
        raise HTTPException(status_code=404, detail="Withdraw request tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/withdraw_requests.html",
        {
            "request": request,
            "requests": requests_,
            "user_id": user_id,
            "title": f"Withdraw Requests - User {user_id}",
        },
    )


# =========================
# ✅ APPROVE WITHDRAW
# =========================
@router.post("/withdraw/{wd_id}/approve")
def approve_withdraw(
    wd_id: int,
    request: Request,
):
    admin_id = request.state.admin.id  # asumsi middleware admin

    try:
        user_id, amount = crud_withdraw_requests.approve_withdraw(wd_id, admin_id)

        crud_admin_audit_logs.log_admin_action(
            admin_id=admin_id,
            action="approve_withdraw",
            target_type="affiliate_withdraw",
            target_id=wd_id,
            notes=f"user_id={user_id}, amount={amount}",
        )

    except ValueError as e:
        raise HTTPException(400, str(e))

    return RedirectResponse("/affiliate/withdraw-requests/pending", status_code=303)


# =========================
# ❌ REJECT WITHDRAW
# =========================
@router.post("/withdraw/{wd_id}/reject")
def reject_withdraw(
    wd_id: int,
    reason: str = Form(...),
    request: Request = None,
):
    admin_id = request.state.admin.id

    try:
        crud_withdraw_requests.reject_withdraw(wd_id, admin_id, reason)

        crud_admin_audit_logs.log_admin_action(
            admin_id=admin_id,
            action="reject_withdraw",
            target_type="affiliate_withdraw",
            target_id=wd_id,
            notes=reason,
        )

    except ValueError as e:
        raise HTTPException(400, str(e))

    return RedirectResponse("/affiliate/withdraw-requests/pending", status_code=303)


# =========================
# 📋 Semua Audit Logs
# =========================
@router.get("/admin-audit-logs", response_class=HTMLResponse)
def list_audit_logs(request: Request):
    logs = crud_admin_audit_logs.get_all_audit_logs()
    return templates.TemplateResponse(
        "affiliate/admin_audit_logs.html",
        {
            "request": request,
            "logs": logs,
            "title": "Affiliate Admin Audit Logs",
        },
    )


# =========================
# 👤 Audit Logs by Admin
# =========================
@router.get("/admin-audit-logs/admin/{admin_id}", response_class=HTMLResponse)
def audit_logs_by_admin(admin_id: int, request: Request):
    logs = crud_admin_audit_logs.get_audit_logs_by_admin(admin_id)

    if not logs:
        raise HTTPException(status_code=404, detail="Audit log tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/admin_audit_logs.html",
        {
            "request": request,
            "logs": logs,
            "admin_id": admin_id,
            "title": f"Audit Logs - Admin {admin_id}",
        },
    )


# =========================
# 🎯 Audit Logs by Target
# =========================
@router.get(
    "/admin-audit-logs/target/{target_type}/{target_id}",
    response_class=HTMLResponse,
)
def audit_logs_by_target(
    target_type: str,
    target_id: int,
    request: Request,
):
    logs = crud_admin_audit_logs.get_audit_logs_by_target(target_type, target_id)

    if not logs:
        raise HTTPException(status_code=404, detail="Audit log tidak ditemukan")

    return templates.TemplateResponse(
        "affiliate/admin_audit_logs.html",
        {
            "request": request,
            "logs": logs,
            "target_type": target_type,
            "target_id": target_id,
            "title": f"Audit Logs - {target_type} #{target_id}",
        },
    )
