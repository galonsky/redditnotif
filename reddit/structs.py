from dataclasses import dataclass
from typing import Optional


@dataclass
class Comment:
    id: str
    author: str
    body: str
    author_icon: Optional[str]
    timestamp: float
