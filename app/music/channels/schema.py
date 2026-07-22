"""
Channel Schemas
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ChannelBase(BaseModel):
    """Field dasar Channel."""

    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    vermuk: bool = False
    notes: Optional[str] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class ChannelCreate(ChannelBase):
    """Schema untuk membuat channel."""


class ChannelUpdate(ChannelBase):
    """Schema untuk mengubah channel."""


class ChannelBulkDelete(BaseModel):
    """Schema bulk delete."""

    ids: list[int] = Field(..., min_length=1)


class ChannelBulkVermuk(BaseModel):
    """Schema bulk update vermuk."""

    ids: list[int] = Field(..., min_length=1)
    vermuk: bool


class ChannelFilter(BaseModel):
    """Schema filter DataTables."""

    draw: int = 1
    start: int = 0
    length: int = 25

    search: Optional[str] = None
    order_column: str = "created_at"
    order_dir: str = "desc"

    vermuk: Optional[bool] = None