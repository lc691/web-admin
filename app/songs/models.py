from typing import List, Optional

from pydantic import BaseModel


class ExportPreviewPayload(BaseModel):
    duplicate_count: int = 2
    target_count: int = 30
    max_song_per_channel: int = 1
    excluded_channels: Optional[List[int]] = []
    exclude_mode: str = "blacklist"