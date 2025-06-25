from dataclasses import dataclass


@dataclass(frozen=True)
class UserParticipationData:
    status: str
    invited_at: str
    started_at: str | None
    completed_at: str | None
    score: int | None
