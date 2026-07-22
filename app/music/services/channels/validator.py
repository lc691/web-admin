"""
Channel Validator
"""

from app.music.repositories.channels.repository import ChannelRepository


class ChannelValidator:
    """
    Validasi business rule Channel.
    """

    @staticmethod
    def validate_name(name: str) -> str:
        if name is None:
            raise ValueError("Nama channel wajib diisi.")

        name = name.strip()

        if not name:
            raise ValueError("Nama channel wajib diisi.")

        if len(name) > 255:
            raise ValueError("Nama channel maksimal 255 karakter.")

        return name

    @staticmethod
    def validate_email(email: str | None) -> str | None:
        if email is None:
            return None

        email = email.strip().lower()

        if not email:
            return None

        if len(email) > 255:
            raise ValueError("Email maksimal 255 karakter.")

        return email

    @staticmethod
    def validate_notes(notes: str | None) -> str | None:
        if notes is None:
            return None

        notes = notes.strip()

        return notes or None

    @staticmethod
    def validate_password(password: str | None) -> str | None:
        if password is None:
            return None

        password = password.strip()

        return password or None

    @classmethod
    def validate_create(
        cls,
        cursor,
        *,
        name: str,
        email: str | None,
    ) -> None:
        name = cls.validate_name(name)
        email = cls.validate_email(email)

        if ChannelRepository.exists_name(cursor, name):
            raise ValueError("Nama channel sudah digunakan.")

        if email and ChannelRepository.exists_email(cursor, email):
            raise ValueError("Email sudah digunakan.")

    @classmethod
    def validate_update(
        cls,
        cursor,
        *,
        channel_id: int,
        name: str,
        email: str | None,
    ) -> None:
        name = cls.validate_name(name)
        email = cls.validate_email(email)

        if not ChannelRepository.exists(cursor, channel_id):
            raise ValueError("Channel tidak ditemukan.")

        if ChannelRepository.exists_name(
            cursor,
            name,
            exclude_id=channel_id,
        ):
            raise ValueError("Nama channel sudah digunakan.")

        if email and ChannelRepository.exists_email(
            cursor,
            email,
            exclude_id=channel_id,
        ):
            raise ValueError("Email sudah digunakan.")