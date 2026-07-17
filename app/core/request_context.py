from dataclasses import dataclass
from time import time


@dataclass
class RequestContext:
    path: str
    is_public: bool
    start_time: float
    user_id: str | None = None