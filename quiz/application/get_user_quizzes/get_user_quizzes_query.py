from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetUserQuizzesQuery:
    requester_id: UUID
