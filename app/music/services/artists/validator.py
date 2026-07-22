"""
Artist Validator
"""

import re

from fastapi import HTTPException

from app.music.repositories.artists.repository import ArtistRepository


class ArtistValidator:
    """
    Validator Artist.
    """

    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 255

    INVALID_PATTERN = re.compile(r"[<>'\"`]")

    # =====================================================
    # NAME
    # =====================================================

    @classmethod
    def validate_name(cls, name: str) -> str:
        """
        Validasi nama artist.
        """

        if name is None:
            raise HTTPException(
                status_code=400,
                detail="Nama artist wajib diisi.",
            )

        name = name.strip()

        if not name:
            raise HTTPException(
                status_code=400,
                detail="Nama artist tidak boleh kosong.",
            )

        if len(name) < cls.MIN_NAME_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Nama artist minimal {cls.MIN_NAME_LENGTH} karakter.",
            )

        if len(name) > cls.MAX_NAME_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Nama artist maksimal {cls.MAX_NAME_LENGTH} karakter.",
            )

        if cls.INVALID_PATTERN.search(name):
            raise HTTPException(
                status_code=400,
                detail="Nama artist mengandung karakter yang tidak diperbolehkan.",
            )

        return name

    # =====================================================
    # CHANNEL
    # =====================================================

    @staticmethod
    def validate_channel(
        cursor,
        channel_id: int,
    ) -> int:
        """
        Pastikan channel ada.
        """

        channels = ArtistRepository.get_channels(cursor)

        channel_ids = {row["id"] for row in channels}

        if channel_id not in channel_ids:
            raise HTTPException(
                status_code=404,
                detail="Channel tidak ditemukan.",
            )

        return channel_id

    # =====================================================
    # DUPLICATE
    # =====================================================

    @staticmethod
    def validate_duplicate(
        cursor,
        *,
        channel_id: int,
        name: str,
        exclude_id: int | None = None,
    ):
        """
        Pastikan nama artist tidak duplikat
        pada channel yang sama.
        """

        exists = ArtistRepository.exists_by_name(
            cursor=cursor,
            channel_id=channel_id,
            name=name,
            exclude_id=exclude_id,
        )

        if exists:
            raise HTTPException(
                status_code=400,
                detail=f"Artist '{name}' sudah ada pada channel tersebut.",
            )

    # =====================================================
    # CREATE
    # =====================================================

    @classmethod
    def validate_create(
        cls,
        cursor,
        *,
        channel_id: int,
        name: str,
    ):
        """
        Validasi create artist.
        """

        name = cls.validate_name(name)

        cls.validate_channel(
            cursor=cursor,
            channel_id=channel_id,
        )

        cls.validate_duplicate(
            cursor=cursor,
            channel_id=channel_id,
            name=name,
        )

        return {
            "channel_id": channel_id,
            "name": name,
        }

    # =====================================================
    # UPDATE
    # =====================================================

    @classmethod
    def validate_update(
        cls,
        cursor,
        *,
        artist_id: int,
        channel_id: int,
        name: str,
    ):
        """
        Validasi update artist.
        """

        if not ArtistRepository.exists(cursor, artist_id):
            raise HTTPException(
                status_code=404,
                detail="Artist tidak ditemukan.",
            )

        name = cls.validate_name(name)

        cls.validate_channel(
            cursor=cursor,
            channel_id=channel_id,
        )

        cls.validate_duplicate(
            cursor=cursor,
            channel_id=channel_id,
            name=name,
            exclude_id=artist_id,
        )

        return {
            "artist_id": artist_id,
            "channel_id": channel_id,
            "name": name,
        }

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def validate_delete(
        cursor,
        artist_id: int,
    ):
        """
        Pastikan artist ada sebelum dihapus.
        """

        if not ArtistRepository.exists(cursor, artist_id):
            raise HTTPException(
                status_code=404,
                detail="Artist tidak ditemukan.",
            )