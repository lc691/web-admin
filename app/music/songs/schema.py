from pydantic import BaseModel

from app.music.repositories.songs.types import SongStatus


class BulkUpdateStatusRequest(BaseModel):
    ids: list[int]
    status: SongStatus