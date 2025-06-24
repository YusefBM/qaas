from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class ParticipationData:
    participation_id: UUID
    participant_id: UUID
    quiz_id: UUID
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[int] = None
