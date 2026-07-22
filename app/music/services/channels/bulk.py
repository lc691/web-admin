"""
Channel Bulk Service
"""

from fastapi import HTTPException

from app.music.repositories.channels.bulk import ChannelBulkRepository
from app.music.services.channels.validator import validate_channel_id


class ChannelBulkService:
    def __init__(self, cursor):
        self.cursor = cursor
        self.repository = ChannelBulkRepository(cursor)

    def delete(
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
            channel_ids = [
                validate_channel_id(channel_id)
                for channel_id in channel_ids
            ]

            existing = self.repository.count_existing(channel_ids)

            if existing == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Channel tidak ditemukan.",
                )

            self.repository.delete_songs(channel_ids)
            self.repository.delete_artists(channel_ids)
            self.repository.delete_channels(channel_ids)

        except HTTPException:
            raise

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Gagal menghapus channel: {exc}",
            ) from exc