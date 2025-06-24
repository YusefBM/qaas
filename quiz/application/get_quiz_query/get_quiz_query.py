from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetQuizQuery:
    participant_id: UUID
    quiz_id: UUID
