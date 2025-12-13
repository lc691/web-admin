from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.referrals import crud
from app.templates import templates

router = APIRouter(prefix="/referrals", tags=["Referrals"])


# =======================
# 📋 Semua Referral
# =======================
@router.get("", response_class=HTMLResponse)
def list_referrals(request: Request):
    referrals = crud.get_all_referrals()
    return templates.TemplateResponse(
        "referrals/list.html",
        {"request": request, "referrals": referrals, "title": "Daftar Referral"},
    )


# =======================
# 👤 Referral oleh Referrer
# =======================
@router.get("/referrer/{user_id}", response_class=HTMLResponse)
def referrals_by_referrer(user_id: int, request: Request):
    referrals = crud.get_referrals_by_referrer(user_id)
    if not referrals:
        raise HTTPException(status_code=404, detail="Referral tidak ditemukan")

    return templates.TemplateResponse(
        "referrals/by_referrer.html",
        {
            "request": request,
            "referrals": referrals,
            "referrer_user_id": user_id,
            "title": f"Referral oleh User {user_id}",
        },
    )


# =======================
# 🔍 Referral User (siapa yang ngajak)
# =======================
@router.get("/user/{user_id}", response_class=HTMLResponse)
def referral_of_user(user_id: int, request: Request):
    referral = crud.get_referral_of_user(user_id)
    if not referral:
        raise HTTPException(status_code=404, detail="User tidak memiliki referral")

    return templates.TemplateResponse(
        "referrals/user_detail.html",
        {"request": request, "referral": referral, "title": f"Referral User {user_id}"},
    )


from app.referrals import logs_crud


# =======================
# 📜 Referral Logs
# =======================
@router.get("/logs", response_class=HTMLResponse)
def referral_logs(request: Request):
    logs = logs_crud.get_all_referral_logs()
    return templates.TemplateResponse(
        "referrals/logs.html", {"request": request, "logs": logs, "title": "Referral Logs"}
    )


@router.get("/logs/referrer/{user_id}", response_class=HTMLResponse)
def referral_logs_by_referrer(user_id: int, request: Request):
    logs = logs_crud.get_logs_by_referrer(user_id)
    return templates.TemplateResponse(
        "referrals/logs.html",
        {"request": request, "logs": logs, "title": f"Referral Logs User {user_id}"},
    )


from app.referrals import metrics_crud


# =======================
# 📊 Referral Metrics
# =======================
@router.get("/metrics", response_class=HTMLResponse)
def referral_metrics(request: Request):
    metrics = metrics_crud.get_all_referral_metrics()
    return templates.TemplateResponse(
        "referrals/metrics.html",
        {"request": request, "metrics": metrics, "title": "Referral Metrics"},
    )


@router.get("/metrics/referrer/{user_id}", response_class=HTMLResponse)
def referral_metrics_by_referrer(user_id: int, request: Request):
    metrics = metrics_crud.get_metrics_by_referrer(user_id)
    return templates.TemplateResponse(
        "referrals/metrics.html",
        {
            "request": request,
            "metrics": metrics,
            "title": f"Referral Metrics User {user_id}",
            "referrer_user_id": user_id,
        },
    )


from app.referrals import commissions_crud


# =======================
# 💰 Referral Commissions
# =======================
@router.get("/commissions", response_class=HTMLResponse)
def referral_commissions(request: Request):
    commissions = commissions_crud.get_all_commissions()
    return templates.TemplateResponse(
        "referrals/commissions.html",
        {"request": request, "commissions": commissions, "title": "Referral Commissions"},
    )


@router.get("/commissions/upline/{user_id}", response_class=HTMLResponse)
def referral_commissions_by_upline(user_id: int, request: Request):
    commissions = commissions_crud.get_commissions_by_upline(user_id)
    return templates.TemplateResponse(
        "referrals/commissions.html",
        {
            "request": request,
            "commissions": commissions,
            "title": f"Komisi Affiliate User {user_id}",
            "upline_user_id": user_id,
        },
    )
