from datetime import datetime

from .cache import UserCache
from .repository import UserRepository

_repo = UserRepository()
_cache = UserCache()


def list_users(
    *,
    filter: str | None = None,
    limit: int = 5000,
    offset: int = 0,
):
    where: list[str] = ["u.is_active = TRUE"]

    if filter == "vip":
        where += [
            "u.is_vip = TRUE",
            "u.vip_expired IS NOT NULL",
            "u.vip_expired > NOW()",
        ]

    elif filter == "nonvip":
        where.append("""
            (
                u.is_vip = FALSE
                OR u.vip_expired IS NULL
                OR u.vip_expired <= NOW()
            )
            """)

    elif filter == "trial":
        where += [
            "u.trial_given = TRUE",
            "u.vip_purchases = 0",
        ]

    elif filter == "affiliate":
        where.append("u.referrer_user_id IS NOT NULL")

    where_sql = " AND ".join(where)

    return _repo.list(
        where_sql=where_sql,
        params={},
        limit=limit,
        offset=offset,
    )


def get_user(user_id: int) -> dict | None:
    cached = _cache.get(user_id)
    if cached:
        return cached

    user = _repo.get_by_id(user_id)
    if user:
        _cache.set(user_id, user)

    return user


def create_user(
    user_id: int,
    username: str | None,
    first_name: str | None,
    is_vip: bool = False,
):
    _repo.create(user_id, username, first_name, is_vip)
    _cache.clear()  # invalidate all


def update_user(
    id: int,
    username: str | None,
    is_vip: bool,
    vip_expired: datetime | None,
    is_active: bool,
):
    _repo.update(id, username, is_vip, vip_expired, is_active)
    _cache.clear(id)


def delete_user(id: int):
    _repo.delete(id)
    _cache.clear(id)
    _cache.clear()  # safety: invalidate list cache
