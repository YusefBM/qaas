from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserParticipationData:
    status: str
    invited_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    my_score: Optional[int]
