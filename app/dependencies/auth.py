from fastapi import Depends, HTTPException, Request, status


# ==========================================================
# CURRENT JOKI
# ==========================================================

def get_current_joki(
    request: Request,
):

    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Silakan login terlebih dahulu.",
        )

    return user


# ==========================================================
# CURRENT JOKI ID
# ==========================================================

def get_current_joki_id(
    user: dict = Depends(
        get_current_joki
    ),
):

    return user["id"]


# ==========================================================
# CURRENT JOKI NAME
# ==========================================================

def get_current_joki_name(
    user: dict = Depends(
        get_current_joki
    ),
):

    return user["nama"]


# ==========================================================
# CURRENT JOKI CODE
# ==========================================================

def get_current_joki_code(
    user: dict = Depends(
        get_current_joki
    ),
):

    return user["kode"]


# ==========================================================
# CURRENT JOKI SESSION
# ==========================================================

def get_current_joki_session(
    user: dict = Depends(
        get_current_joki
    ),
):

    return user


# ==========================================================
# OPTIONAL LOGIN
# ==========================================================

def get_optional_joki(
    request: Request,
):

    return request.session.get(
        "portal_joki"
    )


# ==========================================================
# ADMIN ONLY
# ==========================================================

def require_admin(
    request: Request,
):

    admin = getattr(request.state, "user", None)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak.",
        )

    return admin