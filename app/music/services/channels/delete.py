"""
Channel Delete Service
"""

from fastapi import HTTPException

from app.music.repositories.channels.repository import ChannelRepository
from app.music.services.channels.validator import validate_channel_id


class ChannelDeleteService:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

        self.repository = ChannelRepository(cursor)

    def execute(
        self,
        channel_id: int,
    ) -> None:
        """
        Delete a channel and all related data.
        """

        try:
            channel_id = validate_channel_id(channel_id)

            channel = self.repository.find_by_id(channel_id)

            if not channel:
                raise HTTPException(
                    status_code=404,
                    detail="Channel tidak ditemukan.",
                )

            self.repository.delete_songs(channel_id)
            self.repository.delete_artists(channel_id)
            self.repository.delete(channel_id)

            self.conn.commit()

        except HTTPException:
            self.conn.rollback()
            raise

        except Exception as exc:
            self.conn.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Gagal menghapus channel: {exc}",
            ) from exc

    def bulk_execute(
        self,
        channel_ids: list[int],
    ) -> None:
        """
        Delete multiple channels.
        """

        if not channel_ids:
            raise HTTPException(
                status_code=400,
                detail="Tidak ada channel yang dipilih.",
            )

        try:
            for channel_id in channel_ids:
                channel_id = validate_channel_id(channel_id)

                self.repository.delete_songs(channel_id)
                self.repository.delete_artists(channel_id)
                self.repository.delete(channel_id)

            self.conn.commit()

        except HTTPException:
            self.conn.rollback()
            raise

        except Exception as exc:
            self.conn.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Gagal menghapus channel: {exc}",
            ) from exc