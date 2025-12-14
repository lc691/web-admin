from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.affiliate import (
    crud,
    crud_abuse_logs,
    crud_admin_actions,
    crud_admin_audit_logs,
    crud_commission_logs,
    crud_withdraw_requests,
)
from app.templates import templates

router = APIRouter(
    prefix="/affiliate",
    tags=["Affiliate"],
)


# =========================
# 📋 Semua Transaksi Affiliate
# =========================
@router.get("/transactions", response_class=HTMLResponse)
def list_affiliate_transactions(request: Request):
    transactions = crud.get_all_transactions()
    return templates.TemplateResponse(
        "affiliate/list.html",
        {
            "request": request,
            "transactions": transactions,
            "title": "Affiliate Transactions",
        },
    )


# =========================
# 👤 Transaksi oleh Referrer
# =========================
@router.get("/transactions/referrer/{user_id}", response_class=HTMLResponse)
def transactions_by_referrer(user_id: int, request: Request):
    transactions = crud.get_transactions_by_referrer(user_id)

    if not transactions:
        raise HTTPException(404, "Tidak ada transaksi untuk referrer ini")

    return templates.TemplateResponse(
        "affiliate/list.html",
        {
            "request": request,
            "transactions": transactions,
            "referrer_user_id": user_id,
            "title": f"Transaksi Affiliate - Referrer {user_id}",
        },
    )


# =========================
# 👥 Transaksi oleh Referred User
# =========================
@router.get("/transactions/referred/{user_id}", response_class=HTMLResponse)
def transactions_by_referred_user(user_id: int, request: Request):
    transactions = crud.get_transactions_by_referred_user(user_id)

    if not transactions:
        raise HTTPException(404, "Tidak ada transaksi untuk user ini")

    return templates.TemplateResponse(
        "affiliate/list.html",
        {
            "request": request,
            "transactions": transactions,
            "referred_user_id": user_id,
            "title": f"Transaksi Affiliate - User {user_id}",
        },
    )


# =========================
# 💎 Transaksi berdasarkan Paket VIP
# =========================
@router.get("/transactions/package/{package_name}", response_class=HTMLResponse)
def transactions_by_package(package_name: str, request: Request):
    transactions = crud.get_transactions_by_package(package_name)

    if not transactions:
        raise HTTPException(404, "Tidak ada transaksi untuk paket ini")

    return templates.TemplateResponse(
        "affiliate/list.html",
        {
            "request": request,
            "transactions": transactions,
            "vip_package_name": package_name,
            "title": f"Transaksi Affiliate - Paket {package_name}",
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
def list_withdraw_requests(request: Request):
    requests_ = crud_withdraw_requests.get_all_withdraw_requests()
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
    requests_ = crud_withdraw_requests.get_pending_withdraw_requests()
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
    requests_ = crud_withdraw_requests.get_withdraw_requests_by_user(user_id)

    if not requests_:
        raise HTTPException(404, "Withdraw request tidak ditemukan")

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
