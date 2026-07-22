"""
Channel Validation Services
"""

import re
from typing import Optional

from fastapi import HTTPException

MAX_CHANNEL_NAME_LENGTH = 255

YOUTUBE_PATTERNS = (
    r"^(https?://)?(www\.)?youtube\.com/.+$",
    r"^(https?://)?m\.youtube\.com/.+$",
    r"^(https?://)?youtu\.be/.+$",
)


def normalize_channel_name(name: str) -> str:
    """
    Normalize channel name by trimming and removing duplicate spaces.
    """

    return " ".join(name.strip().split())


def validate_channel_name(name: str) -> str:
    """
    Validate channel name.
    """

    if name is None:
        raise HTTPException(
            status_code=400,
            detail="Nama channel wajib diisi",
        )

    name = normalize_channel_name(name)

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Nama channel wajib diisi",
        )

    if len(name) > MAX_CHANNEL_NAME_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Nama channel maksimal {MAX_CHANNEL_NAME_LENGTH} karakter",
        )

    return name


def validate_channel_id(channel_id: int) -> int:
    """
    Validate channel id.
    """

    if channel_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID channel tidak valid",
        )

    return channel_id


def validate_youtube_url(url: Optional[str]) -> Optional[str]:
    """
    Validate YouTube URL.
    """

    if url is None:
        return None

    url = url.strip()

    if not url:
        return None

    for pattern in YOUTUBE_PATTERNS:
        if re.match(pattern, url, flags=re.IGNORECASE):
            return url

    raise HTTPException(
        status_code=400,
        detail="URL YouTube tidak valid",
    )