"""
Channel Create Service
"""

from fastapi import HTTPException

from app.music.repositories.channels.repository import ChannelRepository
from app.music.repositories.channels.search import ChannelSearchRepository
from app.music.services.channels.validator import (
    validate_channel_name,
    validate_youtube_url,
)


class ChannelCreateService:
    def __init__(self, cursor):
        self.cursor = cursor

        self.repository = ChannelRepository(cursor)
        self.search = ChannelSearchRepository(cursor)

    def execute(
        self,
        name: str,
        youtube_url: str | None = None,
    ) -> int:
        """
        Create a new channel.

        Returns:
            int: New channel ID.
        """

        try:
            name = validate_channel_name(name)
            youtube_url = validate_youtube_url(youtube_url)

            if self.search.exists(name):
                raise HTTPException(
                    status_code=400,
                    detail="Channel dengan nama tersebut sudah ada.",
                )

            return self.repository.create(
                name=name,
                youtube_url=youtube_url,
            )

        except HTTPException:
            raise

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Gagal membuat channel: {exc}",
            ) from exc