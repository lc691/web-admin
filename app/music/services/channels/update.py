"""
Channel Update Service
"""

from fastapi import HTTPException

from app.music.repositories.channels.repository import ChannelRepository
from app.music.repositories.channels.search import ChannelSearchRepository
from app.music.services.channels.validator import (
    validate_channel_id,
    validate_channel_name,
    validate_youtube_url,
)


class ChannelUpdateService:
    def __init__(self, cursor):
        self.cursor = cursor

        self.repository = ChannelRepository(cursor)
        self.search = ChannelSearchRepository(cursor)

    def execute(
        self,
        channel_id: int,
        name: str,
        youtube_url: str | None = None,
    ) -> None:
        """
        Update an existing channel.
        """

        try:
            channel_id = validate_channel_id(channel_id)
            name = validate_channel_name(name)
            youtube_url = validate_youtube_url(youtube_url)

            if not self.repository.find_by_id(channel_id):
                raise HTTPException(
                    status_code=404,
                    detail="Channel tidak ditemukan.",
                )

            if self.search.exists(
                name=name,
                exclude_id=channel_id,
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Channel dengan nama tersebut sudah ada.",
                )

            self.repository.update(
                channel_id=channel_id,
                name=name,
                youtube_url=youtube_url,
            )

        except HTTPException:
            raise

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Gagal mengupdate channel: {exc}",
            ) from exc